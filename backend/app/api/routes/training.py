# backend/app/api/routes/training.py

from fastapi import APIRouter, BackgroundTasks
from app.services.camera_manager import camera_manager
from app.services.hand_detector import hand_detector
from app.services.feature_processor import feature_processor
from app.utils.data_collector import data_collector # Użyjemy istniejącej klasy
from app.utils.image_processor import image_processor # Użyjemy image processor
import cv2
import time
import os
import asyncio
from pydantic import BaseModel

router = APIRouter(prefix="/training", tags=["training"])

# Stan sesji treningowej
training_state = {
    "is_collecting": False,
    "current_gesture": None,
    "samples_collected": 0,
    "target_samples": 0,
    "is_training_model": False
}

class CollectionRequest(BaseModel):
    gesture_name: str
    num_samples: int = 50

@router.post("/collect/start")
async def start_collection(request: CollectionRequest, background_tasks: BackgroundTasks):
    """Start collecting data in background"""
    if training_state["is_collecting"]:
        return {"status": "error", "message": "Already collecting"}
    
    training_state["is_collecting"] = True
    training_state["current_gesture"] = request.gesture_name
    training_state["target_samples"] = request.num_samples
    training_state["samples_collected"] = 0
    
    # Uruchom pętlę zbierania w tle
    background_tasks.add_task(collect_data_loop, request.gesture_name, request.num_samples)
    
    return {"status": "started", "gesture": request.gesture_name}

@router.post("/collect/stop")
async def stop_collection():
    training_state["is_collecting"] = False
    return {"status": "stopped"}

@router.get("/status")
async def get_status():
    return training_state

async def collect_data_loop(gesture_name: str, target: int):
    """Background loop to collect frames"""
    # Setup folder
    save_dir = f"./data/collected/{gesture_name}"
    os.makedirs(save_dir, exist_ok=True)
    
    while training_state["is_collecting"] and training_state["samples_collected"] < target:
        frame = camera_manager.get_frame(0)
        if frame is not None:
            # Detect hand first (don't save empty frames)
            rgb, results = hand_detector.detect_hands(frame)
            landmarks = hand_detector.extract_landmarks(results)
            
            if landmarks:
                timestamp = int(time.time() * 1000)
                filename = f"{save_dir}/{gesture_name}_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                
                training_state["samples_collected"] += 1
                # Small delay to avoid duplicates
                await asyncio.sleep(0.1)
            else:
                # No hand - wait a bit
                await asyncio.sleep(0.1)
        else:
            await asyncio.sleep(0.1)
    
    training_state["is_collecting"] = False

@router.post("/train")
async def trigger_training(background_tasks: BackgroundTasks):
    """Trigger model retraining"""
    if training_state["is_training_model"]:
        return {"status": "error", "message": "Already training"}
    
    training_state["is_training_model"] = True
    background_tasks.add_task(run_training_process)
    return {"status": "started"}

def run_training_process():
    """Run full training pipeline"""
    try:
        # 1. Process images
        print("Processing images...")
        image_processor.process_dataset_structure('./data/collected')
        image_processor.combine_processed_data('combined_all_datasets.npz')
        
        # 2. Train model
        # Tu musielibyśmy zaimportować funkcję train z train_model.py
        # Ale dla uproszczenia wywołamy skrypt systemowy (brzydkie ale skuteczne na szybko)
        print("Training model...")
        os.system("python scripts/train_model.py")
        
    except Exception as e:
        print(f"Training failed: {e}")
    finally:
        training_state["is_training_model"] = False
