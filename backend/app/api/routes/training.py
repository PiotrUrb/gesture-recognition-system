# backend/app/api/routes/training.py
"""
Endpoints do:
- zbierania danych do trenowania (z kamery, z wykorzystaniem hand_detector)
- wywołania trenowania modelu (scripts/train_model.py)
- podglądu statusu i ewentualnych metryk

Uproszczone: tylko lista gestów, zbieranie danych, trenowanie.
"""

import asyncio
import time
import json
import subprocess
from pathlib import Path
from typing import Optional, Literal

import cv2
from fastapi import APIRouter, BackgroundTasks, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.gesture import Gesture
from app.services.camera_manager import camera_manager
from app.services.hand_detector import hand_detector
from app.utils.image_processor import image_processor

router = APIRouter(prefix="/training", tags=["training"])

# -------------------- STAN GLOBALNY --------------------


class TrainingState(BaseModel):
    is_collecting: bool = False
    current_gesture: Optional[str] = None
    samples_collected: int = 0
    target_samples: int = 0
    is_training: bool = False
    training_status: Literal["idle", "preparing", "training", "complete", "error"] = "idle"
    training_progress: int = 0
    training_error: Optional[str] = None
    last_metrics: Optional[dict] = None


# jeden globalny state w module
_training_state = TrainingState()


def get_training_state() -> TrainingState:
    # zwracamy referencję – modyfikujemy bezpośrednio
    return _training_state


# -------------------- MODELE REQUESTÓW --------------------


class CollectRequest(BaseModel):
    gesture_name: str
    num_samples: int = 100


# -------------------- POMOCNICZE --------------------


VALID_GESTURES = [
    "fist",
    "five_fingers",
    "four_fingers",
    "ok_sign",
    "one_finger",
    "open_hand",
    "three_fingers",
    "two_fingers",
]


# -------------------- ENDPOINTY – ZBIERANIE DANYCH --------------------


@router.post("/collect/start")
async def start_collection(
    request: CollectRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Start asynchronicznego zbierania danych dla wybranego gestu.
    Zapisuje tylko klatki, na których wykryto dłoń.
    """
    state = get_training_state()

    if state.is_collecting:
        raise HTTPException(status_code=400, detail="Already collecting data")
    if state.is_training:
        raise HTTPException(status_code=400, detail="Training in progress")

    if request.gesture_name not in VALID_GESTURES:
        raise HTTPException(status_code=400, detail=f"Unknown gesture: {request.gesture_name}")

    # aktualizacja stanu
    state.is_collecting = True
    state.current_gesture = request.gesture_name
    state.target_samples = max(1, request.num_samples)
    state.samples_collected = 0

    # upewniamy się, że gest istnieje w bazie (ASYNC, bez .query)
    result = await db.execute(
        select(Gesture).where(Gesture.name == request.gesture_name)
    )
    gesture = result.scalar_one_or_none()

    if gesture is None:
        gesture = Gesture(
            name=request.gesture_name,
            category="static",
            description=f"Gesture {request.gesture_name}",
            is_default=True,
            enabled=True,
        )
        db.add(gesture)
        await db.commit()
        await db.refresh(gesture)

    # background task
    background_tasks.add_task(_collect_data_loop, request.gesture_name, state.target_samples)

    return {
        "status": "collecting",
        "gesture": request.gesture_name,
        "target_samples": state.target_samples,
    }


@router.post("/collect/stop")
async def stop_collection():
    """Zatrzymanie zbierania danych."""
    state = get_training_state()
    if not state.is_collecting:
        raise HTTPException(status_code=400, detail="Not collecting")

    state.is_collecting = False
    return {"status": "stopped"}


@router.get("/status")
async def get_status():
    """Zwraca aktualny stan kolekcji i trenowania."""
    state = get_training_state()
    return state.dict()


async def _collect_data_loop(gesture_name: str, target: int):
    """
    Funkcja w tle, która pobiera klatki z kamery i zapisuje tylko te z wykrytą dłonią.
    """
    state = get_training_state()

    save_dir = Path("data") / "collected" / gesture_name
    save_dir.mkdir(parents=True, exist_ok=True)

    print(f"[COLLECT] Start collecting for {gesture_name}, target={target}")

    try:
        while state.is_collecting and state.samples_collected < target:
            frame = camera_manager.get_frame(0)
            if frame is None:
                await asyncio.sleep(0.05)
                continue

            # detekcja dłoni
            rgb, results = hand_detector.detect_hands(frame)
            if results and results.multi_hand_landmarks:
                timestamp = int(time.time() * 1000)
                idx = state.samples_collected
                filename = save_dir / f"{gesture_name}_{timestamp}_{idx}.jpg"
                cv2.imwrite(str(filename), frame)
                state.samples_collected += 1
                print(f"[COLLECT] {gesture_name}: {state.samples_collected}/{target}")
                await asyncio.sleep(0.2)  # małe opóźnienie, żeby nie spamować

            else:
                # brak dłoni – szybki sleep
                await asyncio.sleep(0.05)

    except Exception as e:
        print(f"[COLLECT] Error: {e}")
    finally:
        state.is_collecting = False
        print(f"[COLLECT] Finished for {gesture_name}, collected={state.samples_collected}")


# -------------------- ENDPOINTY – TRENING --------------------


@router.post("/train")
async def trigger_training(background_tasks: BackgroundTasks):
    """
    Wywołanie procesu trenowania:
    1. Przetworzenie obrazów -> .npz
    2. Połączenie danych
    3. Uruchomienie scripts/train_model.py
    """
    state = get_training_state()
    if state.is_training:
        raise HTTPException(status_code=400, detail="Training already in progress")
    if state.is_collecting:
        raise HTTPException(status_code=400, detail="Stop collection before training")

    state.is_training = True
    state.training_status = "preparing"
    state.training_progress = 0
    state.training_error = None
    state.last_metrics = None

    background_tasks.add_task(_run_training_pipeline)

    return {"status": "started"}


@router.get("/train/status")
async def get_training_status():
    """Zwraca status trenowania i ewentualne metryki."""
    state = get_training_state()
    return {
        "is_training": state.is_training,
        "status": state.training_status,
        "progress": state.training_progress,
        "error": state.training_error,
        "metrics": state.last_metrics,
    }


@router.get("/metrics")
async def get_metrics():
    """
    Zwraca metryki z pliku models/metrics.json (jeśli skrypt trenowania je zapisuje).
    """
    metrics_path = Path("models") / "metrics.json"
    if not metrics_path.exists():
        raise HTTPException(status_code=404, detail="No metrics available yet")

    try:
        with metrics_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _run_training_pipeline():
    """
    Synchronizowana funkcja wywoływana w tle:
    - przetwarza zebrane dane
    - uruchamia skrypt trenowania
    """
    state = get_training_state()

    try:
        print("[TRAIN] Starting pipeline...")
        state.training_status = "preparing"
        state.training_progress = 10

        # 1. Przetwarzanie obrazów
        print("[TRAIN] Step 1/3: process_dataset_structure")
        image_processor.process_dataset_structure("data/collected")
        state.training_progress = 40

        # 2. Łączenie danych
        print("[TRAIN] Step 2/3: combine_processed_data")
        image_processor.combine_processed_data("combined_all_datasets.npz")
        state.training_progress = 60

        # 3. Trenowanie modelu – korzystamy z istniejącego scripts/train_model.py
        print("[TRAIN] Step 3/3: run train_model.py")
        state.training_status = "training"
        state.training_progress = 70

        result = subprocess.run(
            ["python", "scripts/train_model.py"],
            capture_output=True,
            text=True,
            timeout=900,  # 15 minut
        )

        if result.returncode != 0:
            print("[TRAIN] Script stderr:", result.stderr)
            raise RuntimeError("Training script failed")

        print("[TRAIN] Training script output:")
        print(result.stdout)

        # Próba wczytania metryk
        metrics_path = Path("models") / "metrics.json"
        if metrics_path.exists():
            with metrics_path.open("r", encoding="utf-8") as f:
                state.last_metrics = json.load(f)
        else:
            state.last_metrics = {"status": "completed"}

        state.training_status = "complete"
        state.training_progress = 100
        print("[TRAIN] Pipeline finished successfully")

    except subprocess.TimeoutExpired:
        state.training_error = "Training timeout exceeded"
        state.training_status = "error"
        print("[TRAIN] Error: training timeout")

    except Exception as e:
        state.training_error = str(e)
        state.training_status = "error"
        print(f"[TRAIN] Error: {e}")

    finally:
        state.is_training = False
