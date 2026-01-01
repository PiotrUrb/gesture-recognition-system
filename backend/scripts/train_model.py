# backend/scripts/train_model.py

"""
Train gesture recognition model
"""

import sys
import os
import json
from pathlib import Path

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
)
import joblib

backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)


def load_dataset(dataset_path: str):
    """Load processed dataset"""
    print(f"\n[DATA] Loading dataset: {dataset_path}")
    data = np.load(dataset_path, allow_pickle=True)
    features = data["features"]
    labels = data["labels"]

    print(f"  Features shape: {features.shape}")
    print(f"  Total samples: {len(labels)}")
    print(f"  Unique gestures: {len(set(labels))}")
    return features, labels


def prepare_data(features, labels):
    """Prepare data for training"""
    print("\n[DATA] Preparing data...")

    # Encode labels
    label_encoder = LabelEncoder()
    labels_encoded = label_encoder.fit_transform(labels)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        features,
        labels_encoded,
        test_size=0.2,
        random_state=42,
        stratify=labels_encoded,
    )

    print(f"  Train samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")
    print(f"  Classes: {len(label_encoder.classes_)}")
    return X_train, X_test, y_train, y_test, label_encoder


def train_model(X_train, y_train):
    """Train Random Forest model"""
    print("\n[TRAIN] Training Random Forest model...")
    print("        (This may take a few minutes depending on dataset size)")

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=100,
        min_samples_split=10,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
        verbose=1,
    )

    model.fit(X_train, y_train)
    print("[TRAIN] Training complete!")
    return model


def evaluate_model(model, X_test, y_test, label_encoder):
    """Evaluate model performance"""
    print("\n[EVAL] Evaluating model...")

    # Predictions
    y_pred = model.predict(X_test)

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\n[EVAL] Accuracy: {accuracy * 100:.2f}%")

    # Classification report
    print("\n[EVAL] Classification Report:")
    print(
        classification_report(
            y_test,
            y_pred,
            target_names=label_encoder.classes_,
            zero_division=0,
        )
    )

    # Confusion matrix
    print("\n[EVAL] Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred)
    print(cm)

    return accuracy, y_pred


def save_model(
    model,
    label_encoder,
    accuracy,
    output_dir: str = "./models",
):
    """Save trained model and metadata"""
    print("\n[SAVE] Saving model artifacts...")

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save model
    model_file = output_path / "gesture_model.pkl"
    joblib.dump(model, model_file)
    print(f"  Model saved: {model_file}")

    # Save label encoder
    encoder_file = output_path / "label_encoder.pkl"
    joblib.dump(label_encoder, encoder_file)
    print(f"  Encoder saved: {encoder_file}")

    # Save metadata
    metadata = {
        "accuracy": float(accuracy),
        "num_classes": len(label_encoder.classes_),
        "classes": label_encoder.classes_.tolist(),
        "model_type": "RandomForestClassifier",
        "num_estimators": 100,
        "feature_dim": 83,
    }

    metadata_file = output_path / "model_metadata.json"
    with metadata_file.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)
    print(f"  Metadata saved: {metadata_file}")

    print(f"\n[SAVE] Model package saved to: {output_path}")


def main():
    print("\n" + "=" * 60)
    print("GESTURE RECOGNITION MODEL TRAINING")
    print("=" * 60)

    # Load dataset
    dataset_path = "./data/processed/combined_all_datasets.npz"
    if not os.path.exists(dataset_path):
        print(f"\n[ERROR] Dataset not found: {dataset_path}")
        print("        Please run: python scripts/process_all_datasets.py")
        return

    features, labels = load_dataset(dataset_path)

    # Prepare data
    X_train, X_test, y_train, y_test, label_encoder = prepare_data(
        features, labels
    )

    # Train
    model = train_model(X_train, y_train)

    # Evaluate
    accuracy, y_pred = evaluate_model(
        model, X_test, y_test, label_encoder
    )

    # Save
    save_model(model, label_encoder, accuracy)

    # Summary
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE")
    print("=" * 60)

    print("\n[SUMMARY]")
    print(f"  Accuracy: {accuracy * 100:.2f}%")
    print("  Model: Random Forest (100 trees)")
    print(f"  Classes: {len(label_encoder.classes_)}")
    print(f"  Train samples: {len(X_train)}")
    print(f"  Test samples: {len(X_test)}")

    print("\n  Model files:")
    print("   - models/gesture_model.pkl")
    print("   - models/label_encoder.pkl")
    print("   - models/model_metadata.json")

    print("\nNext step: Test model live:")
    print("  python scripts/test_model_live.py")


if __name__ == "__main__":
    main()
