/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Settings, FileText, Hand, Maximize, X,
  ChevronRight, Sliders, AlertTriangle, Eye, Hash
} from 'lucide-react';
import api from '../services/api';

// Widget Kamery - UJEDNOLICONY
const CameraGridWidget = ({ onMaximize }: { onMaximize: () => void }) => {
  const navigate = useNavigate();

  return (
    <div className="bg-black rounded-xl border border-gray-700 overflow-hidden relative h-full min-h-[400px] flex flex-col group shadow-lg shadow-black/50">
      {/* Overlay - UJEDNOLICONY z LiveView */}
      <div className="absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/90 to-transparent z-10 flex justify-between items-start opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div className="flex items-center gap-2">
          <span className="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded animate-pulse">LIVE</span>
          <h3 className="text-white font-medium text-xs shadow-black drop-shadow-md">Main Feed</h3>
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
          <div className="w-1.5 h-1.5 rounded-full bg-green-500"></div>
          CAM-01 • USB • 1280x720
        </span>
        <button onClick={() => navigate('/cameras')} className="flex items-center gap-1 text-[10px] text-accent-blue hover:text-white transition-colors font-medium uppercase tracking-wide">
          <Settings size={10} /> Camera Settings
        </button>
      </div>
    </div>
  );
};

// Widget Gestów
const GesturesWidget = () => {
  const navigate = useNavigate();
  const gestures = [
    { name: 'Fist', type: 'STOP', icon: '✊', color: 'text-red-400', border: 'border-red-500' },
    { name: 'Open Hand', type: 'START', icon: '✋', color: 'text-green-400', border: 'border-green-500' },
    { name: 'Index Point', type: 'SELECT', icon: '👉', color: 'text-blue-400', border: 'border-blue-500' },
    { name: 'OK Sign', type: 'CONFIRM', icon: '👌', color: 'text-yellow-400', border: 'border-yellow-500' },
  ];

  return (
    <div className="bg-industrial-gray p-4 rounded-xl border border-gray-700 h-full flex flex-col shadow-lg min-h-[300px]">
      <div className="flex justify-between items-center mb-4 shrink-0 pb-2 border-b border-gray-700/50">
        <h3 className="font-bold text-white flex items-center gap-2 text-sm">
          <Hand className="text-yellow-500" size={18} /> Active Gestures
        </h3>
        <button onClick={() => navigate('/training')} className="p-1.5 hover:bg-gray-700 rounded-lg transition-colors text-gray-400 hover:text-white">
          <Settings size={16} />
        </button>
      </div>
      <div className="flex-1 overflow-y-auto space-y-2 pr-1 custom-scrollbar min-h-0">
        {gestures.map(g => (
          <div 
            key={g.name} 
            onClick={() => navigate('/training')}
            className={`bg-gray-800/40 hover:bg-gray-800 p-3 rounded-lg border-l-[3px] ${g.border} flex items-center justify-between group cursor-pointer transition-all border-t border-r border-b border-transparent hover:border-gray-600`}
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl bg-black/20 w-10 h-10 flex items-center justify-center rounded-md">{g.icon}</span>
              <div>
                <p className="text-sm font-bold text-gray-200">{g.name}</p>
                <p className={`text-[10px] uppercase font-bold tracking-wider ${g.color} opacity-80`}>{g.type}</p>
              </div>
            </div>
            <ChevronRight size={16} className="text-gray-700 group-hover:text-white transition-colors" />
          </div>
        ))}
      </div>
      <button onClick={() => navigate('/training')} className="mt-4 w-full py-2.5 border border-dashed border-gray-600 text-gray-500 text-xs rounded-lg hover:border-accent-blue hover:text-accent-blue hover:bg-accent-blue/5 transition-colors uppercase tracking-wide font-bold">
        + Add New Gesture (Training)
      </button>
    </div>
  );
};

// Widget Parametrów
const ParametersWidget = ({ info }: { info: any }) => {
  const navigate = useNavigate();
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
            <span className="text-2xl font-bold text-white">{info?.max_cameras || 1}</span>
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Cameras</span>
          </div>
          <div className="bg-black/20 p-3 rounded border border-gray-700 flex flex-col items-center justify-center text-center">
            <Hash className="text-gray-500 mb-1" size={16} />
            <span className="text-2xl font-bold text-white">1,240</span>
            <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Detected</span>
          </div>
          <div className="bg-black/20 p-3 rounded border border-gray-700 flex flex-col items-center justify-center text-center col-span-2 flex-row gap-4">
             <div className="flex items-center gap-2">
                <AlertTriangle className="text-red-500" size={18} />
                <span className="text-xl font-bold text-red-400">0</span>
             </div>
             <span className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">Active Alerts</span>
          </div>
        </div>

        <div className="space-y-3 pt-2 border-t border-gray-700/50">
            <div>
                <div className="flex justify-between text-xs text-gray-400 mb-1.5 font-medium">
                <span>Sensitivity</span>
                <span className="text-white">75%</span>
                </div>
                <div className="w-full bg-gray-800 h-2 rounded-full overflow-hidden border border-gray-700">
                <div className="bg-blue-500 h-2 rounded-full w-3/4 shadow-[0_0_10px_#3b82f6]"></div>
                </div>
            </div>
            <div className="flex justify-between items-center">
                <span className="text-xs text-gray-400">Active Mode</span>
                <span className="text-[10px] font-bold text-green-400 bg-green-500/10 px-2 py-0.5 rounded border border-green-500/20 tracking-wide">STANDARD</span>
            </div>
        </div>

        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-gray-700/50">
          <div className="bg-black/20 p-2 rounded border border-gray-700">
            <span className="text-[9px] text-gray-500 block uppercase font-bold tracking-wide">Algorithm</span>
            <span className="text-xs font-mono text-gray-300">RandomForest</span>
          </div>
          <div className="bg-black/20 p-2 rounded border border-gray-700">
            <span className="text-[9px] text-gray-500 block uppercase font-bold tracking-wide">Model Ver.</span>
            <span className="text-xs font-mono text-gray-300">{info?.version || 'v1.0.0'}</span>
          </div>
        </div>
      </div>

      <button onClick={() => navigate('/settings')} className="mt-4 w-full py-2 bg-gray-700 hover:bg-gray-600 text-white text-xs font-bold rounded-lg transition-colors flex items-center justify-center gap-2">
        <Settings size={14} /> Advanced Settings
      </button>
    </div>
  );
};

// Widget Logów
const LogsWidget = () => {
  const navigate = useNavigate();
  const [logs, setLogs] = useState<any[]>([]);
  
  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const res = await api.get('/api/v1/gestures/logs');
        setLogs(res.data.slice(0, 10));
      } catch (e) { console.error(e); }
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
          <span className="text-xs font-bold text-gray-300 uppercase tracking-wide">System Event Logs</span>
        </div>
        <button onClick={() => navigate('/analytics')} className="text-[10px] font-medium text-accent-blue hover:text-white transition-colors bg-blue-500/10 px-3 py-1 rounded hover:bg-blue-500/20">
          View Full History
        </button>
      </div>
      <div className="flex-1 overflow-y-auto custom-scrollbar bg-black/20 p-0">
        <table className="w-full text-left text-[11px] table-fixed border-collapse">
          <thead className="bg-gray-800/30 text-gray-500 border-b border-gray-700/50 sticky top-0">
              <tr>
                  <th className="py-2 px-4 w-24 font-medium">Time</th>
                  <th className="py-2 px-4 w-32 font-medium">Event</th>
                  <th className="py-2 px-4 w-24 font-medium">Mode</th>
                  <th className="py-2 px-4 w-20 font-medium">Conf.</th>
                  <th className="py-2 px-4 font-medium">Message</th>
              </tr>
          </thead>
          <tbody className="text-gray-400 divide-y divide-gray-800/50">
            {logs.length === 0 ? (
                <tr><td colSpan={5} className="py-8 text-center opacity-50 italic">Waiting for events...</td></tr>
            ) : (
                logs.map((log, idx) => (
                <tr key={log.id} className={`hover:bg-white/5 transition-colors ${idx === 0 ? 'bg-accent-blue/5' : ''}`}>
                    <td className="py-2 px-4 font-mono text-gray-500">{new Date(log.timestamp).toLocaleTimeString()}</td>
                    <td className="py-2 px-4 font-bold text-white flex items-center gap-2">
                        <div className="w-1.5 h-1.5 rounded-full bg-accent-blue"></div>
                        {log.gesture}
                    </td>
                    <td className="py-2 px-4"><span className="bg-gray-700/50 border border-gray-600 px-1.5 py-0.5 rounded text-gray-300 uppercase text-[9px] font-bold tracking-wide">{log.mode}</span></td>
                    <td className="py-2 px-4 text-gray-400">{(log.confidence * 100).toFixed(0)}%</td>
                    <td className="py-2 px-4 opacity-70 truncate">Action executed successfully</td>
                </tr>
                ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

// Modal Pełnoekranowy - UJEDNOLICONY
const FullScreenCameraModal = ({ isOpen, onClose }: { isOpen: boolean, onClose: () => void }) => {
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
            <h2 className="text-white font-bold text-lg drop-shadow-md pl-2">Fullscreen Feed</h2>
            <button 
              onClick={onClose} 
              className="pointer-events-auto bg-red-600 hover:bg-red-500 text-white p-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-bold"
            >
              <X size={18} /> CLOSE
            </button>
        </div>
        <img src="http://localhost:8000/api/v1/cameras/0/stream" className="w-full h-full object-contain" alt="FullScreen Stream" />
      </div>
    </div>
  );
};

// Główny Dashboard
const Dashboard = () => {
  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [isCameraExpanded, setIsCameraExpanded] = useState(false);

  useEffect(() => {
    api.get('/info').then(res => setSystemInfo(res.data)).catch(() => {});
  }, []);

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
            <ParametersWidget info={systemInfo} />
          </div>
        </div>
      </div>
      <FullScreenCameraModal isOpen={isCameraExpanded} onClose={() => setIsCameraExpanded(false)} />
    </>
  );
};

export default Dashboard;
