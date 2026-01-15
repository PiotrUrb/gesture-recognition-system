/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { Grid3x3, Grid2x2, Square, Maximize2, Settings, X, Maximize } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import api from '../services/api';
import DetectionInfo from '../components/DetectionInfo';

type GridMode = '1x1' | '2x1' | '2x2' | '3x3' | 'auto';
type DetectionMode = 'standard' | 'safe' | 'all';

const LiveView = () => {
  const navigate = useNavigate();
  const [cameras, setCameras] = useState<any[]>([]);
  const [gridMode, setGridMode] = useState<GridMode>('3x3');
  const [detectionMode, setDetectionMode] = useState<DetectionMode>('standard');
  const [selectedCamera, setSelectedCamera] = useState<number>(0);
  const [fullscreenCamera, setFullscreenCamera] = useState<number | null>(null);

  useEffect(() => {
    const fetchCameras = async () => {
      try {
        const res = await api.get('/api/v1/cameras/');
        setCameras(res.data.cameras || []);
      } catch (e) {
        console.error(e);
      }
    };
    fetchCameras();
    const interval = setInterval(fetchCameras, 10000);
    return () => clearInterval(interval);
  }, []);

  const handleModeChange = async (mode: DetectionMode) => {
    try {
      await api.post('/api/v1/cameras/mode', { mode });
      setDetectionMode(mode);
    } catch (e) {
      console.error(e);
    }
  };

  const getGridLayout = () => {
    const count = cameras.length;
    
    if (gridMode !== 'auto') {
      switch (gridMode) {
        case '1x1': return { cols: 1, maxCameras: 1 };
        case '2x1': return { cols: 2, maxCameras: 2 };
        case '2x2': return { cols: 2, maxCameras: 4 };
        case '3x3': return { cols: 3, maxCameras: 9 };
        default: return { cols: 3, maxCameras: 9 };
      }
    }

    if (count <= 1) return { cols: 1, maxCameras: count };
    if (count <= 4) return { cols: 2, maxCameras: count };
    return { cols: 3, maxCameras: count };
  };

  const { cols, maxCameras } = getGridLayout();
  const displayCameras = gridMode === 'auto' ? cameras : cameras.slice(0, maxCameras);

  return (
    <>
      <div className="h-[calc(100vh-5rem)] flex gap-6">
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          
          {/* TOOLBAR */}
          <div className="bg-industrial-gray rounded-xl border border-gray-700 p-4 flex justify-between items-center shadow-lg">
            
            {/* Lewy: Tryby Grid */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400 uppercase font-bold tracking-wider">Camera Grid:</span>
              <div className="flex gap-2 bg-black/30 p-1 rounded-lg">
                {[
                  { mode: '1x1' as GridMode, icon: Square, label: '1×1' },
                  { mode: '2x1' as GridMode, icon: Grid2x2, label: '2×1' },
                  { mode: '2x2' as GridMode, icon: Grid2x2, label: '2×2' },
                  { mode: '3x3' as GridMode, icon: Grid3x3, label: '3×3' },
                ].map(({ mode, icon: Icon, label }) => (
                  <button
                    key={mode}
                    onClick={() => setGridMode(mode)}
                    className={`flex items-center gap-2 px-3 py-2 rounded-lg text-xs font-bold transition-all ${
                      gridMode === mode
                        ? 'bg-accent-blue text-white shadow-md'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    <Icon size={14} />
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Środek: Tryby Detekcji */}
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-400 uppercase font-bold tracking-wider">Detection Mode:</span>
              <div className="flex gap-2 bg-black/30 p-1 rounded-lg">
                {[
                  { mode: 'standard' as DetectionMode, label: 'STANDARD' },
                  { mode: 'safe' as DetectionMode, label: 'SAFE' },
                  { mode: 'all' as DetectionMode, label: 'DETECT ALL' },
                ].map(({ mode, label }) => (
                  <button
                    key={mode}
                    onClick={() => handleModeChange(mode)}
                    className={`px-4 py-2 rounded-lg text-xs font-bold transition-all ${
                      detectionMode === mode
                        ? 'bg-accent-blue text-white shadow-md'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            {/* Prawy: Kontrolki */}
            <div className="flex gap-2">
              <button 
                onClick={() => setFullscreenCamera(selectedCamera)}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
                title="Fullscreen selected camera"
              >
                <Maximize2 size={16} />
              </button>
              <button 
                onClick={() => navigate('/cameras')}
                className="p-2 bg-gray-700 hover:bg-gray-600 rounded-lg text-white transition-colors"
                title="Camera settings"
              >
                <Settings size={16} />
              </button>
            </div>
          </div>

          {/* SIATKA KAMER */}
          <div className="flex-1 overflow-y-auto custom-scrollbar">
            <IntelligentCameraGrid 
              cameras={displayCameras} 
              columns={cols}
              selectedCamera={selectedCamera}
              onSelectCamera={setSelectedCamera}
              onFullscreen={setFullscreenCamera}
            />
          </div>
        </div>

        {/* PRAWY PANEL: DETEKCJA */}
        <div className="w-96 shrink-0">
          <DetectionInfo cameraId={selectedCamera} />
        </div>
      </div>

      {/* MODAL PEŁNOEKRANOWY */}
      {fullscreenCamera !== null && (
        <FullscreenCameraModal 
          camera={cameras.find(c => c.id === fullscreenCamera)} 
          onClose={() => setFullscreenCamera(null)} 
        />
      )}
    </>
  );
};

// Inteligentna siatka
const IntelligentCameraGrid = ({ cameras, columns, selectedCamera, onSelectCamera, onFullscreen }: any) => {
  const rows: any[][] = [];
  for (let i = 0; i < cameras.length; i += columns) {
    rows.push(cameras.slice(i, i + columns));
  }

  return (
    <div className="space-y-4">
      {rows.map((row, rowIdx) => {
        const isIncompleteRow = row.length < columns;
        
        return (
          <div 
            key={rowIdx}
            className={`grid gap-4 ${isIncompleteRow ? 'flex justify-center' : `grid-cols-${columns}`}`}
            style={isIncompleteRow ? { 
              display: 'flex',
              justifyContent: 'center',
              gap: '1rem'
            } : undefined}
          >
            {row.map((cam: any) => (
              <div 
                key={cam.id} 
                style={isIncompleteRow ? { 
                  width: `calc((100% - ${(columns - 1) * 1}rem) / ${columns})`,
                  maxWidth: '500px' 
                } : undefined}
              >
                <CameraFeed 
                  camera={cam} 
                  isSelected={selectedCamera === cam.id}
                  onClick={() => onSelectCamera(cam.id)}
                  onFullscreen={() => onFullscreen(cam.id)}
                />
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
};

// Feed kamery
const CameraFeed = ({ camera, isSelected, onClick, onFullscreen }: any) => {
  return (
    <div 
      onClick={onClick}
      onDoubleClick={onFullscreen}
      className={`bg-black rounded-xl overflow-hidden border-2 transition-all cursor-pointer relative group aspect-video ${
        isSelected ? 'border-accent-blue shadow-lg shadow-blue-900/50' : 'border-gray-700 hover:border-gray-600'
      }`}
    >
      {/* Overlay Header */}
      <div className="absolute top-0 left-0 w-full p-3 bg-gradient-to-b from-black/90 to-transparent z-10 flex justify-between items-start opacity-0 group-hover:opacity-100 transition-opacity duration-300">
        <div className="flex items-center gap-2">
          <span className="bg-red-600 text-white text-[10px] font-bold px-2 py-0.5 rounded animate-pulse">LIVE</span>
          <h3 className="text-white font-medium text-xs">Camera {camera.id}</h3>
        </div>
        <button 
          onClick={(e) => {
            e.stopPropagation();
            onFullscreen();
          }}
          className="bg-black/50 hover:bg-accent-blue p-1.5 rounded text-white transition-colors backdrop-blur-sm border border-white/10"
          title="Fullscreen"
        >
          <Maximize size={16} />
        </button>
      </div>

      {/* Video Stream */}
      <img
        src={`http://localhost:8000/api/v1/cameras/${camera.id}/stream`}
        alt={`Camera ${camera.id}`}
        className="w-full h-full object-cover"
        onError={(e) => {
          e.currentTarget.style.display = 'none';
          const parent = e.currentTarget.parentElement;
          if (parent && !parent.querySelector('.error-placeholder')) {
            const errorDiv = document.createElement('div');
            errorDiv.className = 'error-placeholder absolute inset-0 flex items-center justify-center text-gray-500 bg-gray-900';
            errorDiv.innerHTML = '<span class="text-sm">Stream unavailable</span>';
            parent.appendChild(errorDiv);
          }
        }}
      />

      {/* Footer Info */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-2 text-[10px] text-gray-400 font-mono">
        {camera.actual_width}×{camera.actual_height} • {camera.actual_fps}fps
      </div>
    </div>
  );
};

// Modal pełnoekranowy
const FullscreenCameraModal = ({ camera, onClose }: { camera: any, onClose: () => void }) => {
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  if (!camera) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/95 backdrop-blur-sm flex items-center justify-center p-6 animate-fade-in">
      <div className="relative w-full h-full bg-black rounded-2xl border border-gray-800 overflow-hidden shadow-2xl shadow-black flex flex-col">
        
        {/* Header - UJEDNOLICONY */}
        <div className="absolute top-0 left-0 w-full p-4 bg-gradient-to-b from-black/80 to-transparent z-20 flex justify-between items-center pointer-events-none">
          <h2 className="text-white font-bold text-lg drop-shadow-md pl-2">Fullscreen Feed - Camera {camera.id}</h2>
          <button 
            onClick={onClose}
            className="pointer-events-auto bg-red-600 hover:bg-red-500 text-white p-2 rounded-lg shadow-lg transition-colors flex items-center gap-2 text-sm font-bold"
          >
            <X size={18} /> CLOSE
          </button>
        </div>

        {/* Video Stream */}
        <img 
          src={`http://localhost:8000/api/v1/cameras/${camera.id}/stream`} 
          className="w-full h-full object-contain" 
          alt={`Fullscreen Camera ${camera.id}`}
          onError={(e) => {
            e.currentTarget.style.display = 'none';
            const parent = e.currentTarget.parentElement;
            if (parent && !parent.querySelector('.error-message')) {
              const errorDiv = document.createElement('div');
              errorDiv.className = 'error-message absolute inset-0 flex items-center justify-center text-center text-gray-500 bg-gray-900';
              errorDiv.innerHTML = '<p class="text-2xl mb-2">Stream Unavailable</p><p class="text-sm">Camera disconnected or stream error</p>';
              parent.appendChild(errorDiv);
            }
          }}
        />
      </div>
    </div>
  );
};

export default LiveView;
