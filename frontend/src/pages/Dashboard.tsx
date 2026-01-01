/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Settings,
  FileText,
  Hand,
  Maximize,
  X,
  ChevronRight,
  Sliders,
  AlertTriangle,
  Eye,
  Hash,
} from 'lucide-react';
import api from '../services/api';

// --- GESTURES CONFIG ---

const STATIC_GESTURES = [
  'fist',
  'open_hand',
  'one_finger',
  'two_fingers',
  'three_fingers',
  'four_fingers',
  'five_fingers',
  'ok_sign',
] as const;

const GESTURE_ICONS: Record<string, string> = {
  fist: '✊',
  open_hand: '✋',
  ok_sign: '👌',
  one_finger: '1',
  two_fingers: '2',
  three_fingers: '3',
  four_fingers: '4',
  five_fingers: '5',
};

const GESTURE_COLORS: Record<
  string,
  { border: string; bg: string; text: string }
> = {
  fist: { border: 'border-red-500', bg: 'bg-red-500/10', text: 'text-red-400' },
  open_hand: {
    border: 'border-green-500',
    bg: 'bg-green-500/10',
    text: 'text-green-400',
  },
  one_finger: {
    border: 'border-blue-500',
    bg: 'bg-blue-500/10',
    text: 'text-blue-400',
  },
  two_fingers: {
    border: 'border-purple-500',
    bg: 'bg-purple-500/10',
    text: 'text-purple-400',
  },
  three_fingers: {
    border: 'border-pink-500',
    bg: 'bg-pink-500/10',
    text: 'text-pink-400',
  },
  four_fingers: {
    border: 'border-indigo-500',
    bg: 'bg-indigo-500/10',
    text: 'text-indigo-400',
  },
  five_fingers: {
    border: 'border-cyan-500',
    bg: 'bg-cyan-500/10',
    text: 'text-cyan-400',
  },
  ok_sign: {
    border: 'border-yellow-500',
    bg: 'bg-yellow-500/10',
    text: 'text-yellow-400',
  },
};

// --- CAMERA WIDGET ---

const CameraGridWidget = ({ onMaximize }: { onMaximize: () => void }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-black rounded-xl border border-gray-700 overflow-hidden relative h-full min-h-[400px] flex flex-col group shadow-lg shadow-black/50">
      {/* Overlay */}
      <div className="absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/90 to-transparent z-10 flex justify-between items-start opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div className="flex items-center gap-2">
          <span className="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded animate-pulse">
            LIVE
          </span>
          <h3 className="text-white font-medium text-xs shadow-black drop-shadow-md">
            Main Feed
          </h3>
        </div>
        <button
          onClick={onMaximize}
          className="bg-black/50 hover:bg-accent-blue p-1.5 rounded text-white transition-colors backdrop-blur-sm border border-white/10"
        >
          <Maximize size={16} />
        </button>
      </div>

      {/* Obraz */}
      <div className="flex-1 bg-gray-900 relative flex items-center justify-center overflow-hidden">
        <img
          src="http://localhost:8000/api/v1/cameras/0/stream"
          className="w-full h-full object-contain max-h-full"
          alt="Live Stream"
        />
      </div>

      {/* Pasek dolny */}
      <div className="bg-gray-900/95 border-t border-gray-800 p-2 flex justify-between items-center shrink-0 h-8">
        <span className="text-[10px] text-gray-400 font-mono flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500" />
          CAM-01 • USB • 1280x720
        </span>
        <button
          onClick={() => navigate('/cameras')}
          className="flex items-center gap-1 text-[10px] text-accent-blue hover:text-white transition-colors font-medium uppercase tracking-wide"
        >
          <Settings size={10} /> Camera Settings
        </button>
      </div>
    </div>
  );
};

// --- ACTIVE GESTURES ---

const GesturesWidget = () => {
  const navigate = useNavigate();
  const [allGestures, setAllGestures] = useState<any[]>([]);
  const [lastDetectedGesture, setLastDetectedGesture] = useState<string | null>(
    null,
  );
  const [detectionTime, setDetectionTime] = useState<Date | null>(null);

  useEffect(() => {
    const fetchGestures = async () => {
      try {
        const res = await api.get('/api/v1/gestures/default');
        const gestures = (res.data.gestures || []).filter((g: any) =>
          STATIC_GESTURES.includes(g.name),
        );
        setAllGestures(
          gestures.length
            ? gestures
            : STATIC_GESTURES.map((name) => ({ name, action: null })),
        );
      } catch {
        setAllGestures(
          STATIC_GESTURES.map((name) => ({ name, action: null })),
        );
      }
    };

    const pollRecentGesture = async () => {
      try {
        const res = await api.get('/api/v1/gesture-logs/recent?limit=1');
        const logs = res.data.logs || [];
        if (logs.length > 0) {
          setLastDetectedGesture(logs[0].gesture);
          setDetectionTime(new Date(logs[0].timestamp));
        }
      } catch {
        /* ignore */
      }
    };

    fetchGestures();
    pollRecentGesture();
    const interval = setInterval(pollRecentGesture, 500);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-industrial-gray p-4 rounded-xl border border-gray-700 h-full flex flex-col shadow-lg min-h-[300px]">
      <div className="flex justify-between items-center mb-4 shrink-0 pb-2 border-b border-gray-700/50">
        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
          <Hand className="text-yellow-500" size={18} /> Active Gestures
        </h3>
      </div>

      {/* Aktualnie wykryty gest */}
      {lastDetectedGesture && (
        <div className="mb-4 p-3 rounded-lg border-2 border-green-500 bg-green-500/10 animate-pulse">
          <div className="text-xs text-green-300 font-bold uppercase mb-2">
            ▶ DETECTED NOW
          </div>
          <div className="flex items-center gap-3">
            <span className="text-4xl">
              {GESTURE_ICONS[lastDetectedGesture] || '🖐️'}
            </span>
            <div>
              <p className="text-white font-bold capitalize">
                {lastDetectedGesture.replace('_', ' ')}
              </p>
              <p className="text-[10px] text-gray-400">
                {detectionTime?.toLocaleTimeString()}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Lista gestów */}
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar min-h-0">
        {allGestures.map((g) => {
          const colors = GESTURE_COLORS[g.name] || GESTURE_COLORS.fist;
          const isDetected = lastDetectedGesture === g.name;

          return (
            <div
              key={g.name}
              onClick={() => navigate('/training')}
              className={`p-3 rounded-lg border-l-[3px] flex items-center justify-between group cursor-pointer transition-all border-t border-r border-b ${
                isDetected
                  ? `${colors.border} ${colors.bg} border-l-[4px] ring-2 ring-offset-1 ring-offset-gray-900 ${colors.text} font-bold`
                  : 'border-gray-600 bg-gray-800/40 hover:bg-gray-800 border-transparent hover:border-gray-600'
              }`}
            >
              <div className="flex items-center gap-3">
                <span className="text-2xl bg-black/20 w-10 h-10 flex items-center justify-center rounded-md">
                  {GESTURE_ICONS[g.name] || '🖐️'}
                </span>
                <div>
                  <p className="text-sm font-bold text-gray-200">
                    {g.name.replace('_', ' ')}
                  </p>
                  <p
                    className={`text-[10px] uppercase font-bold tracking-wider ${colors.text} opacity-80`}
                  >
                    {g.action || g.category || 'ACTION'}
                  </p>
                </div>
              </div>
              <ChevronRight
                size={16}
                className={`${
                  isDetected ? colors.text : 'text-gray-700 group-hover:text-white'
                } transition-colors`}
              />
            </div>
          );
        })}
      </div>

      {/* Start Training */}
      <button
        onClick={() => navigate('/training')}
        className="mt-4 w-full py-2.5 border border-gray-600 text-gray-200 text-xs rounded-lg hover:border-accent-blue hover:text-accent-blue hover:bg-accent-blue/5 transition-colors uppercase tracking-wide font-bold"
      >
        Start Training
      </button>
    </div>
  );
};

// --- SYSTEM INFO ---

const ParametersWidget = () => {
  const [systemInfo, setSystemInfo] = useState<{
    max_cameras: number;
    version: string;
  }>({
    max_cameras: 1,
    version: 'v1.0.0',
  });
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // podstawowe info – /health lub /info
        try {
          const res = await api.get('/health');
          if (res.data) {
            setSystemInfo({
              max_cameras: res.data.max_cameras ?? 1,
              version: res.data.version ?? 'v1.0.0',
            });
          }
        } catch {
          try {
            const res = await api.get('/info');
            if (res.data) {
              setSystemInfo({
                max_cameras: res.data.max_cameras ?? 1,
                version: res.data.version ?? 'v1.0.0',
              });
            }
          } catch {
            // zostaw domyślne
          }
        }

        // statystyki gestów
        try {
          const res = await api.get('/api/v1/gesture-logs/stats');
          if (res.data?.stats) setStats(res.data.stats);
        } catch {
          /* optional */
        }
      } catch {
        /* ignore */
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  const avg = stats?.average_confidence
    ? (stats.average_confidence * 100).toFixed(1)
    : '75.0';

  return (
    <div className="bg-industrial-gray p-4 rounded-xl border border-gray-700 h-full min-h-[250px] flex flex-col shadow-lg">
      <div className="flex justify-between items-center mb-4 shrink-0">
        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
          <Sliders className="text-blue-400" size={18} /> System Info
        </h3>
      </div>

      <div className="space-y-4 flex-1 overflow-y-auto custom-scrollbar">
        <div className="grid grid-cols-2 gap-3">
          <div className="bg-black/20 p-3 rounded border border-gray-700 flex flex-col items-center justify-center text-center">
            <Eye className="text-gray-500 mb-1" size={16} />
            <span className="text-2xl font-bold text-white">
              {systemInfo.max_cameras}
            </span>
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">
              Cameras
            </span>
          </div>

          <div className="bg-black/20 p-3 rounded border border-gray-700 flex flex-col items-center justify-center text-center">
            <Hash className="text-gray-500 mb-1" size={16} />
            <span className="text-2xl font-bold text-white">
              {stats?.total_detections ?? 0}
            </span>
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">
              Detections
            </span>
          </div>

          <div className="bg-black/20 p-3 rounded border border-gray-700 flex flex-col items-center justify-center text-center col-span-2">
            <AlertTriangle className="text-gray-500 mb-1" size={16} />
            <span className="text-xs text-gray-400 mb-1">Model accuracy</span>
            <span className="text-lg font-bold text-emerald-400">{avg}%</span>
          </div>
        </div>

        <div className="border-t border-gray-700/50 pt-3 grid grid-cols-2 gap-2">
          <div className="bg-black/20 p-2 rounded border border-gray-700">
            <span className="text-[9px] text-gray-500 block uppercase font-bold tracking-wide">
              Algorithm
            </span>
            <span className="text-xs font-mono text-gray-300">RandomForest</span>
          </div>
          <div className="bg-black/20 p-2 rounded border border-gray-700">
            <span className="text-[9px] text-gray-500 block uppercase font-bold tracking-wide">
              Model Ver.
            </span>
            <span className="text-xs font-mono text-gray-300">
              {systemInfo.version}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

// --- LOGS ---

const LogsWidget = () => {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<any[]>([]);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get('/api/v1/gesture-logs/recent?limit=10');
        setLogs(res.data.logs || []);
      } catch {
        /* ignore */
      }
    };

    const interval = setInterval(fetchLogs, 2000);
    fetchLogs();
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-industrial-gray rounded-xl border border-gray-700 h-full overflow-hidden flex flex-col shadow-lg min-h-[200px]">
      <div className="bg-gray-800/50 px-4 py-3 border-b border-gray-700 flex justify-between items-center shrink-0">
        <div className="flex items-center gap-2">
          <FileText className="text-gray-400" size={16} />
          <span className="text-xs font-bold text-gray-300 uppercase tracking-wide">
            System Event Logs
          </span>
        </div>
        <button
          onClick={() => navigate('/analytics')}
          className="text-[10px] font-medium text-accent-blue hover:text-white transition-colors bg-blue-500/10 px-3 py-1 rounded hover:bg-blue-500/20"
        >
          View Full History
        </button>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar bg-black/20 p-0">
        <table className="w-full text-left text-[11px] table-fixed border-collapse">
          <thead className="bg-gray-800/30 text-gray-500 border-b border-gray-700/50 sticky top-0">
            <tr>
              <th className="py-2 px-4 w-24 font-medium">Time</th>
              <th className="py-2 px-4 w-32 font-medium">Event</th>
              <th className="py-2 px-4 w-20 font-medium">Conf.</th>
              <th className="py-2 px-4 font-medium">Message</th>
            </tr>
          </thead>
          <tbody className="text-gray-400 divide-y divide-gray-800/50">
            {logs.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  className="py-8 text-center opacity-50 italic"
                >
                  Waiting for events...
                </td>
              </tr>
            ) : (
              logs.map((log, idx) => (
                <tr
                  key={log.id || idx}
                  className={`hover:bg-white/5 transition-colors ${
                    idx === 0 ? 'bg-accent-blue/5' : ''
                  }`}
                >
                  <td className="py-2 px-4 font-mono text-gray-500">
                    {new Date(log.timestamp).toLocaleTimeString()}
                  </td>
                  <td className="py-2 px-4 font-bold text-white flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-accent-blue" />
                    {log.gesture}
                  </td>
                  <td className="py-2 px-4 text-gray-400">
                    {typeof log.confidence === 'number'
                      ? (log.confidence * 100).toFixed(0)
                      : '—'}
                    %
                  </td>
                  <td className="py-2 px-4 opacity-70 truncate">
                    {log.message || 'Gesture detected'}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// --- FULLSCREEN MODAL ---

const FullScreenCameraModal = ({
  isOpen,
  onClose,
}: {
  isOpen: boolean;
  onClose: () => void;
}) => {
  useEffect(() => {
    if (!isOpen) return;

    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm flex items-center justify-center p-6 animate-fade-in">
      <div className="relative w-full h-full bg-black rounded-2xl border border-gray-800 overflow-hidden shadow-2xl shadow-black flex flex-col">
        <div className="absolute top-0 left-0 w-full p-4 bg-gradient-to-b from-black/80 to-transparent z-20 flex justify-between items-center pointer-events-none">
          <h2 className="text-white font-bold text-lg drop-shadow-md pl-2">
            Fullscreen Feed
          </h2>
          <button
            onClick={onClose}
            className="pointer-events-auto bg-red-600 hover:bg-red-500 text-white p-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-bold"
          >
            <X size={18} /> CLOSE
          </button>
        </div>
        <img
          src="http://localhost:8000/api/v1/cameras/0/stream"
          className="w-full h-full object-contain"
          alt="FullScreen Stream"
        />
      </div>
    </div>
  );
};

// --- MAIN DASHBOARD ---

const Dashboard = () => {
  const [isCameraExpanded, setIsCameraExpanded] = useState(false);

  return (
    <>
      <div className="grid grid-cols-12 gap-6 pb-8">
        <div className="col-span-12 lg:col-span-9 flex flex-col gap-6">
          <div className="aspect-video min-h-[400px] shadow-xl shadow-black/30 rounded-xl">
            <CameraGridWidget onMaximize={() => setIsCameraExpanded(true)} />
          </div>
          <div className="h-[300px]">
            <LogsWidget />
          </div>
        </div>

        <div className="col-span-12 lg:col-span-3 flex flex-col gap-6">
          <div className="h-[500px]">
            <GesturesWidget />
          </div>
          <div className="h-auto">
            <ParametersWidget />
          </div>
        </div>
      </div>
      <FullScreenCameraModal
        isOpen={isCameraExpanded}
        onClose={() => setIsCameraExpanded(false)}
      />
    </>
  );
};

export default Dashboard;
