import React, { useEffect, useState } from "react";
import VideoPlayer from "../components/VideoPlayer";
import type {
  TrainingStateDto,
  TrainingStatusName,
  TrainingMetrics,
} from "../services/trainingService";
import { trainingService } from "../services/trainingService";
import {
  Play,
  Square,
  Rocket,
  Loader2,
} from "lucide-react";

const GESTURES = [
  "fist",
  "five_fingers",
  "four_fingers",
  "ok_sign",
  "one_finger",
  "open_hand",
  "three_fingers",
  "two_fingers",
];

const Training: React.FC = () => {
  const [selectedGesture, setSelectedGesture] = useState<string>(GESTURES[0]);
  const [numSamples, setNumSamples] = useState<number>(100);

  const [status, setStatus] = useState<TrainingStateDto | null>(null);
  const [error, setError] = useState<string | null>(null);

  // polling statusu co 1s
  useEffect(() => {
    const fetchStatus = async (): Promise<void> => {
      try {
        const s = await trainingService.getStatus();
        setStatus(s);
      } catch (e: unknown) {
        console.error(e);
      }
    };

    fetchStatus();
    const interval = window.setInterval(fetchStatus, 1000);

    return () => {
      window.clearInterval(interval);
    };
  }, []);

  const handleStartCollect = async (): Promise<void> => {
    try {
      setError(null);
      await trainingService.startCollection(selectedGesture, numSamples);
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError("Failed to start collection");
      }
    }
  };

  const handleStopCollect = async (): Promise<void> => {
    try {
      setError(null);
      await trainingService.stopCollection();
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError("Failed to stop collection");
      }
    }
  };

  const handleStartTraining = async (): Promise<void> => {
    try {
      setError(null);
      await trainingService.startTraining();
    } catch (e: unknown) {
      if (e instanceof Error) {
        setError(e.message);
      } else {
        setError("Failed to start training");
      }
    }
  };

  const collecting = status?.collecting ?? false;
  const samplesCollected = status?.samples_collected ?? 0;
  const targetSamples = status?.target_samples ?? numSamples;
  const collectionProgress =
    targetSamples > 0
      ? Math.min(100, Math.round((samplesCollected / targetSamples) * 100))
      : 0;

  const trainingStatus: TrainingStatusName = status?.training_status ?? "idle";
  const trainingProgress = status?.training_progress ?? 0;
  const trainingError = status?.training_error ?? null;
  const metrics: TrainingMetrics | null = status?.last_metrics ?? null;

  const trainingStatusLabel = (): string => {
    switch (trainingStatus) {
      case "preparing":
        return "Preparing data…";
      case "training":
        return "Training model…";
      case "complete":
        return "Training complete!";
      case "error":
        return "Training error";
      default:
        return "Idle";
    }
  };

  const isTrainingActive =
    trainingStatus === "preparing" || trainingStatus === "training";

  return (
    <div className="flex flex-col gap-6">
      {/* PAGE HEADER */}
      <div className="flex flex-col gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">
            Model Training
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Collect gesture samples and train the recognition model
          </p>
        </div>

        {error && (
          <div className="flex items-center justify-between rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            <div className="flex items-center gap-2">
              <span className="text-base">✖</span>
              <span>{error}</span>
            </div>
            <button
              className="text-xs font-semibold underline hover:text-red-100"
              onClick={() => setError(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {trainingError && (
          <div className="flex items-center gap-2 rounded-xl border border-red-500/40 bg-red-500/10 px-4 py-3 text-sm text-red-200">
            <span className="text-base">✖</span>
            <span>{trainingError}</span>
          </div>
        )}
      </div>

      {/* MAIN GRID: Camera + Controls */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1">
        {/* LEFT: CAMERA (wider) */}
        <div className="lg:col-span-2 bg-[#111318] border border-gray-700 rounded-xl p-4 flex flex-col gap-4">
          <div>
            <h2 className="text-sm font-semibold text-gray-100">
              Live Camera
            </h2>
            <p className="text-xs text-gray-400 mt-1">
              Position your hand clearly in frame
            </p>
          </div>
          <div className="flex-1 min-h-[300px] overflow-hidden rounded-lg border border-gray-700 bg-black">
            <VideoPlayer cameraId={0} />
          </div>
        </div>

        {/* RIGHT: CONTROLS */}
        <div className="flex flex-col gap-4">
          {/* GESTURES */}
          <div className="bg-[#111318] border border-gray-700 rounded-xl p-4">
            <h3 className="text-sm font-semibold text-gray-100 mb-3">
              Select Gesture
            </h3>
            <div className="grid grid-cols-2 gap-2">
              {GESTURES.map((g) => (
                <button
                  key={g}
                  type="button"
                  onClick={() => setSelectedGesture(g)}
                  disabled={collecting || status?.is_training}
                  className={`text-xs rounded-lg border px-2.5 py-2 font-medium capitalize transition ${
                    selectedGesture === g
                      ? "border-blue-500 bg-blue-500/20 text-blue-100"
                      : "border-gray-700 bg-black/30 text-gray-200 hover:border-blue-400 hover:bg-blue-500/10"
                  } disabled:opacity-40 disabled:cursor-not-allowed`}
                >
                  {g.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          {/* COLLECTION */}
          <div className="bg-[#111318] border border-gray-700 rounded-xl p-4 flex flex-col gap-3">
            <h3 className="text-sm font-semibold text-gray-100">
              Data Collection
            </h3>

            <div className="flex items-center gap-2 text-xs">
              <label className="text-gray-300 whitespace-nowrap">Samples</label>
              <input
                type="number"
                min={10}
                max={500}
                value={numSamples}
                disabled={collecting || status?.is_training}
                onChange={(e) => setNumSamples(Number(e.target.value) || 0)}
                className="flex-1 rounded-md border border-gray-700 bg-black/40 px-2 py-1.5 text-xs text-gray-100 focus:border-blue-400 focus:outline-none focus:ring-1 focus:ring-blue-400 disabled:opacity-40"
              />
            </div>

            <div>
              <div className="flex items-center justify-between text-xs mb-1.5 text-gray-400">
                <span>{samplesCollected}/{targetSamples}</span>
                <span>{collectionProgress}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gray-800 overflow-hidden">
                <div
                  className="h-2 rounded-full bg-emerald-500 transition-all"
                  style={{ width: `${collectionProgress}%` }}
                />
              </div>
            </div>

            <div className="flex gap-2 pt-1">
              {!collecting ? (
                <button
                  type="button"
                  onClick={handleStartCollect}
                  disabled={status?.is_training}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-md bg-blue-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-blue-500 disabled:cursor-not-allowed disabled:bg-gray-600"
                >
                  <Play size={14} />
                  Start
                </button>
              ) : (
                <button
                  type="button"
                  onClick={handleStopCollect}
                  className="inline-flex flex-1 items-center justify-center gap-2 rounded-md bg-red-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-red-500"
                >
                  <Square size={14} />
                  Stop
                </button>
              )}
            </div>
          </div>

          {/* TRAINING */}
          <div className="bg-[#111318] border border-gray-700 rounded-xl p-4 flex flex-col gap-3">
            <h3 className="text-sm font-semibold text-gray-100">
              Train Model
            </h3>

            <div>
              <div className="flex items-center justify-between text-xs mb-1.5 text-gray-400">
                <span>{trainingStatusLabel()}</span>
                <span>{trainingProgress}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-gray-800 overflow-hidden">
                <div
                  className={`h-2 rounded-full ${
                    trainingStatus === "error"
                      ? "bg-red-500"
                      : trainingStatus === "complete"
                      ? "bg-emerald-500"
                      : "bg-blue-500"
                  } transition-all`}
                  style={{ width: `${trainingProgress}%` }}
                />
              </div>
            </div>

            <button
              type="button"
              onClick={handleStartTraining}
              disabled={
                collecting || status?.is_training || samplesCollected === 0
              }
              className="inline-flex w-full items-center justify-center gap-2 rounded-md bg-emerald-600 px-3 py-2.5 text-xs font-semibold text-white shadow-sm hover:bg-emerald-500 disabled:cursor-not-allowed disabled:bg-gray-600"
            >
              {isTrainingActive ? (
                <Loader2 className="animate-spin" size={14} />
              ) : (
                <Rocket size={14} />
              )}
              {isTrainingActive ? "Training..." : "Start Training"}
            </button>
          </div>

          {/* METRICS */}
          {metrics && (
            <div className="bg-[#111318] border border-green-500/30 rounded-xl p-4">
              <div className="text-xs font-semibold text-green-200 mb-3">
                ✓ Model Metrics
              </div>
              <div className="space-y-2">
                {typeof metrics.accuracy === "number" && (
                  <MetricRow
                    label="Accuracy"
                    value={(metrics.accuracy * 100).toFixed(1) + "%"}
                  />
                )}
                {typeof metrics.precision === "number" && (
                  <MetricRow
                    label="Precision"
                    value={(metrics.precision * 100).toFixed(1) + "%"}
                  />
                )}
                {typeof metrics.recall === "number" && (
                  <MetricRow
                    label="Recall"
                    value={(metrics.recall * 100).toFixed(1) + "%"}
                  />
                )}
                {typeof metrics.f1_score === "number" && (
                  <MetricRow
                    label="F1"
                    value={(metrics.f1_score * 100).toFixed(1) + "%"}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const MetricRow: React.FC<{ label: string; value: string }> = ({
  label,
  value,
}) => (
  <div className="flex items-center justify-between text-xs text-gray-300">
    <span>{label}</span>
    <span className="font-semibold text-gray-50">{value}</span>
  </div>
);

export default Training;
