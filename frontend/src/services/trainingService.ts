const API_BASE_URL = "http://localhost:8000/api/v1";


export type TrainingStatusName =
  | "idle"
  | "preparing"
  | "training"
  | "complete"
  | "error";

export interface TrainingMetrics {
  accuracy?: number;
  precision?: number;
  recall?: number;
  f1_score?: number;
  // możesz dodać inne pola jeśli backend je zwraca
}

export interface TrainingStateDto {
  collecting: boolean;
  current_gesture: string | null;
  samples_collected: number;
  target_samples: number;
  is_training: boolean;
  training_status: TrainingStatusName;
  training_progress: number;
  training_error: string | null;
  last_metrics: TrainingMetrics | null;
}

class TrainingService {
  async startCollection(
    gestureName: string,
    numSamples: number
  ): Promise<unknown> {
    const res = await fetch(`${API_BASE_URL}/training/collect/start`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        gesture_name: gestureName,
        num_samples: numSamples,
      }),
    });

    if (!res.ok) {
      const data = (await res.json().catch(() => ({}))) as {
        detail?: string;
      };
      throw new Error(data.detail || "Failed to start collection");
    }

    return res.json();
  }

  async stopCollection(): Promise<unknown> {
    const res = await fetch(`${API_BASE_URL}/training/collect/stop`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      const data = (await res.json().catch(() => ({}))) as {
        detail?: string;
      };
      throw new Error(data.detail || "Failed to stop collection");
    }

    return res.json();
  }

  async getStatus(): Promise<TrainingStateDto> {
    const res = await fetch(`${API_BASE_URL}/training/status`);
    if (!res.ok) {
      throw new Error("Failed to get training status");
    }
    return res.json();
  }

  async startTraining(): Promise<unknown> {
    const res = await fetch(`${API_BASE_URL}/training/train`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!res.ok) {
      const data = (await res.json().catch(() => ({}))) as {
        detail?: string;
      };
      throw new Error(data.detail || "Failed to start training");
    }

    return res.json();
  }

  async getTrainingStatus(): Promise<{
    is_training: boolean;
    status: TrainingStatusName;
    progress: number;
    error: string | null;
    metrics: TrainingMetrics | null;
  }> {
    const res = await fetch(`${API_BASE_URL}/training/train/status`);
    if (!res.ok) {
      throw new Error("Failed to get train status");
    }
    return res.json();
  }

  async getMetrics(): Promise<TrainingMetrics> {
    const res = await fetch(`${API_BASE_URL}/training/metrics`);
    if (!res.ok) {
      throw new Error("Failed to get metrics");
    }
    return res.json();
  }
}

export const trainingService = new TrainingService();
