/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  Hand, Plus, Settings, TrendingUp, Trash2, GraduationCap, 
  RefreshCw, X, Camera, Check, AlertCircle, Loader, 
  Upload, Download, Image as ImageIcon, 
  Cpu, History, Eye, Play, StopCircle
} from 'lucide-react';
// import api from '../services/api'; // Usunięto, bo używamy mocków

// --- TYPY ---
interface Gesture {
  id: number;
  name: string;
  category: string;
  description: string;
  machine_action: string;
  is_default: boolean;
  enabled: boolean;
  confidence_threshold: number;
  samples_count: number;
  trained: boolean;
  accuracy: number;
  detections: number;
}

interface SampleImage {
  id: number;
  url: string;
  timestamp: string;
}

type ViewMode = 'overview' | 'collecting' | 'gallery' | 'training';

const Training = () => {
  // State
  const [gestures, setGestures] = useState<Gesture[]>([]);
  const [selectedGestureId, setSelectedGestureId] = useState<number | null>(null);
  const [viewMode, setViewMode] = useState<ViewMode>('overview');
  const [showAddModal, setShowAddModal] = useState(false);
  const [loading, setLoading] = useState(false);

  // Derived state
  const selectedGesture = gestures.find(g => g.id === selectedGestureId);

  // Mock Data Load - zdefiniowane przed useEffect
  const fetchGestures = useCallback(async () => {
    setLoading(true);
    try {
      setTimeout(() => {
        setGestures(getDemoGestures());
        setLoading(false);
      }, 500);
    } catch (e) {
      console.error(e);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGestures();
  }, [fetchGestures]);

  // Handlers
  const handleSelectGesture = (id: number | null) => {
    setSelectedGestureId(id);
    setViewMode('overview');
  };

  const updateGestureConfig = (id: number, updates: Partial<Gesture>) => {
    setGestures(prev => prev.map(g => g.id === id ? { ...g, ...updates } : g));
  };

  const deleteGesture = (id: number) => {
    setGestures(prev => prev.filter(g => g.id !== id));
    setSelectedGestureId(null);
    setViewMode('overview');
  };

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col lg:flex-row gap-3 lg:gap-6 overflow-hidden p-3 lg:p-6">
      
      {/* --- LEWY PANEL (LISTA) --- */}
      <div className="w-full lg:w-80 flex-shrink-0 bg-industrial-gray rounded-xl border border-gray-700 flex flex-col shadow-lg h-auto lg:h-full max-h-[35vh] lg:max-h-full">
        
        {/* Header Listy */}
        <div className="p-4 border-b border-gray-700 flex justify-between items-center bg-gray-800/50 flex-shrink-0">
          <h3 className="font-bold text-white flex items-center gap-2 text-sm lg:text-base">
            <Hand className="text-accent-blue flex-shrink-0" size={20} />
            <span className="hidden sm:inline">Gesture Library</span>
            <span className="sm:hidden">Library</span>
          </h3>
          <button 
            onClick={() => setShowAddModal(true)}
            className="p-1.5 bg-blue-600 hover:bg-blue-500 rounded-lg text-white transition-colors flex-shrink-0"
            title="Add New Gesture"
          >
            <Plus size={18} />
          </button>
        </div>

        {/* Lista */}
        <div className="flex-1 overflow-y-auto p-2 space-y-2 custom-scrollbar min-h-0">
          
          {/* Opcja Globalna (System) */}
          <div 
            onClick={() => handleSelectGesture(null)}
            className={`p-3 rounded-lg cursor-pointer transition-all border flex items-center gap-3 ${
              selectedGestureId === null
                ? 'bg-purple-900/20 border-purple-500/50' 
                : 'bg-gray-800/40 border-transparent hover:bg-gray-700'
            }`}
          >
            <div className="p-2 bg-purple-500/20 rounded-md text-purple-400 flex-shrink-0">
              <Cpu size={18} />
            </div>
            <div className="min-w-0 flex-1">
              <p className={`text-xs lg:text-sm font-bold truncate ${selectedGestureId === null ? 'text-white' : 'text-gray-300'}`}>
                System & Models
              </p>
              <p className="text-[9px] text-gray-500 truncate">Global</p>
            </div>
          </div>

          <div className="h-px bg-gray-700 my-2 mx-2" />

          {/* Lista Gestów */}
          {gestures.map((gesture) => (
            <GestureListItem 
              key={gesture.id} 
              gesture={gesture} 
              isSelected={selectedGestureId === gesture.id}
              onClick={() => handleSelectGesture(gesture.id)}
            />
          ))}
        </div>
      </div>

      {/* --- PRAWY PANEL (GŁÓWNY OBSZAR) --- */}
      <div className="flex-1 bg-industrial-gray rounded-xl border border-gray-700 flex flex-col shadow-lg min-w-0 overflow-hidden h-auto lg:h-full max-h-[65vh] lg:max-h-full">
        {loading ? (
          <div className="flex-1 flex items-center justify-center">
            <Loader className="animate-spin text-accent-blue" size={48} />
          </div>
        ) : selectedGestureId === null ? (
          <GlobalSystemView gestures={gestures} />
        ) : (
          <GestureWorkspace 
            gesture={selectedGesture!} 
            mode={viewMode}
            setMode={setViewMode}
            onUpdate={(updates: any) => updateGestureConfig(selectedGesture!.id, updates)}
            onDelete={() => deleteGesture(selectedGesture!.id)}
          />
        )}
      </div>

      {/* Modal Dodawania */}
      {showAddModal && <AddGestureModal onClose={() => setShowAddModal(false)} onAdded={fetchGestures} />}
    </div>
  );
};

// --- WIDOK 1: GLOBAL SYSTEM DASHBOARD ---
const GlobalSystemView = ({ gestures }: { gestures: Gesture[] }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImportModel = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append('model_file', file);
    try {
      // await api.post('/api/v1/models/import', formData);
      alert('Model imported successfully!');
    } catch {
      alert('Failed to import model');
    }
  };

  const handleExportModel = async () => {
    try {
      // window.open('/api/v1/models/export', '_blank');
      alert('Model export started...');
    } catch {
      alert('Failed to export model');
    }
  };

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-4 lg:p-8">
      <div className="mb-8">
        <h2 className="text-2xl lg:text-3xl font-bold text-white mb-2">AI Model Management</h2>
        <p className="text-gray-400 text-sm lg:text-base">Manage global training, models history and system accuracy.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 lg:gap-4 mb-8">
        <div className="bg-black/30 p-4 lg:p-5 rounded-xl border border-gray-700">
          <h4 className="text-gray-400 text-[10px] lg:text-xs font-bold uppercase mb-2">Active Model</h4>
          <div className="text-xl lg:text-2xl font-bold text-white mb-1">v2.4.1-RF</div>
          <div className="flex items-center gap-2 text-green-400 text-xs">
            <Check size={12} /> Loaded & Ready
          </div>
        </div>
        <div className="bg-black/30 p-4 lg:p-5 rounded-xl border border-gray-700">
          <h4 className="text-gray-400 text-[10px] lg:text-xs font-bold uppercase mb-2">Total Samples</h4>
          <div className="text-xl lg:text-2xl font-bold text-white mb-1">
            {gestures.reduce((acc, g) => acc + g.samples_count, 0)}
          </div>
          <div className="text-xs text-gray-500">Across {gestures.length} gestures</div>
        </div>
        <div className="bg-black/30 p-4 lg:p-5 rounded-xl border border-gray-700">
          <h4 className="text-gray-400 text-[10px] lg:text-xs font-bold uppercase mb-2">System Accuracy</h4>
          <div className="text-xl lg:text-2xl font-bold text-white mb-1">94.8%</div>
          <div className="w-full bg-gray-700 h-1.5 rounded-full mt-2 overflow-hidden">
            <div className="bg-green-500 h-full w-[94.8%]" />
          </div>
        </div>
      </div>

      <div className="space-y-6">
        <section>
          <h3 className="text-base lg:text-lg font-bold text-white mb-4 flex items-center gap-2">
            <GraduationCap className="text-blue-400 flex-shrink-0" /> Global Actions
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4">
            <ActionButton 
              icon={GraduationCap} 
              label="Train All Gestures" 
              sub="Retrain model with all data"
              color="blue"
              onClick={() => alert('Training all gestures...')}
            />
            <ActionButton 
              icon={RefreshCw} 
              label="Retrain & Update" 
              sub="Append new samples to model"
              color="green"
              onClick={() => alert('Retraining with new data...')}
            />
            <ActionButton 
              icon={Upload} 
              label="Import Model" 
              sub="Load .pkl / .h5 file"
              color="gray"
              onClick={() => fileInputRef.current?.click()}
            />
            <ActionButton 
              icon={Download} 
              label="Export Model" 
              sub="Save current model"
              color="gray"
              onClick={handleExportModel}
            />
            <ActionButton 
              icon={History} 
              label="Model History" 
              sub="Restore previous versions"
              color="gray"
              onClick={() => alert('Model history...')}
            />
          </div>
          <input 
            ref={fileInputRef}
            type="file"
            accept=".pkl,.h5,.pth"
            className="hidden"
            onChange={handleImportModel}
          />
        </section>

        <section className="border-t border-gray-700 pt-6">
          <h3 className="text-base lg:text-lg font-bold text-white mb-4 flex items-center gap-2">
            <AlertCircle className="text-red-400 flex-shrink-0" /> Danger Zone
          </h3>
          <div className="flex flex-col sm:flex-row gap-3">
            <button className="px-4 py-2 bg-red-900/20 border border-red-500/30 text-red-400 rounded-lg hover:bg-red-900/40 transition-colors text-xs lg:text-sm font-bold flex items-center justify-center gap-2 flex-1">
              <Trash2 size={16} /> Delete Current Model
            </button>
            <button className="px-4 py-2 bg-red-900/20 border border-red-500/30 text-red-400 rounded-lg hover:bg-red-900/40 transition-colors text-xs lg:text-sm font-bold flex items-center justify-center gap-2 flex-1">
              <Trash2 size={16} /> Clear All Training Data
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

// --- WIDOK 2: GESTURE WORKSPACE ---
const GestureWorkspace = ({ gesture, mode, setMode, onUpdate, onDelete }: any) => {
  if (mode === 'collecting') {
    return <CollectionMode gesture={gesture} onBack={() => setMode('overview')} />;
  }

  if (mode === 'gallery') {
    return <GalleryMode gesture={gesture} onBack={() => setMode('overview')} />;
  }

  if (mode === 'training') {
    return <TrainingMode gesture={gesture} onBack={() => setMode('overview')} />;
  }

  return (
    <div className="flex-1 overflow-y-auto custom-scrollbar p-4 lg:p-8">
      
      {/* Header Gestu */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8 border-b border-gray-700 pb-6">
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 w-full sm:w-auto">
          <div className="text-5xl lg:text-6xl bg-black/40 w-20 h-20 lg:w-24 lg:h-24 flex items-center justify-center rounded-2xl border-2 border-gray-700 shadow-inner flex-shrink-0">
            {gesture.description?.split(' ')[0] || '✋'}
          </div>
          <div className="min-w-0 flex-1">
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3 mb-1">
              <h2 className="text-2xl lg:text-3xl font-bold text-white break-words">{gesture.name}</h2>
              <span className={`px-2 py-0.5 text-[10px] uppercase font-bold rounded border whitespace-nowrap flex-shrink-0 ${
                gesture.trained 
                  ? 'bg-green-500/10 text-green-400 border-green-500/30' 
                  : 'bg-red-500/10 text-red-400 border-red-500/30'
              }`}>
                {gesture.trained ? 'Model Ready' : 'Needs Training'}
              </span>
            </div>
            <p className="text-gray-400 font-mono text-xs lg:text-sm">{gesture.machine_action}</p>
          </div>
        </div>
        
        {/* Configuration Toggle + Delete */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center gap-2 w-full sm:w-auto">
          <div className="flex items-center bg-black/20 p-2 rounded-lg border border-gray-700 flex-1 sm:flex-none">
            <span className="text-[10px] lg:text-xs font-bold text-gray-400 mr-3 uppercase whitespace-nowrap">Detection:</span>
            <button 
              onClick={() => onUpdate({ enabled: !gesture.enabled })}
              className={`px-3 py-1.5 rounded-md text-xs font-bold transition-colors flex-1 sm:flex-none ${
                gesture.enabled ? 'bg-green-600 text-white' : 'bg-gray-700 text-gray-400'
              }`}
            >
              {gesture.enabled ? 'ENABLED' : 'DISABLED'}
            </button>
          </div>
          
          {/* Delete Gesture Button */}
          <button 
            onClick={() => {
              if (confirm(`Delete gesture "${gesture.name}" permanently? This cannot be undone.`)) {
                onDelete();
              }
            }}
            className="px-3 py-1.5 bg-red-900/20 border border-red-500/30 text-red-400 hover:bg-red-900/40 rounded-lg text-xs font-bold transition-colors whitespace-nowrap"
            title="Delete this gesture permanently"
          >
            Delete Gesture
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 lg:gap-4 mb-8">
        <StatBox label="Samples" value={gesture.samples_count} icon={ImageIcon} color="blue" />
        <StatBox label="Accuracy" value={`${gesture.accuracy}%`} icon={TrendingUp} color="green" />
        <StatBox label="Detections" value={gesture.detections} icon={Eye} color="purple" />
        <StatBox label="Threshold" value={`${(gesture.confidence_threshold * 100).toFixed(0)}%`} icon={Settings} color="gray" />
      </div>

      {/* Configuration Slider */}
      <div className="mb-8 bg-black/20 p-4 lg:p-6 rounded-xl border border-gray-700">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3 mb-4">
          <span className="text-xs lg:text-sm text-gray-300 font-bold">Sensitivity Threshold</span>
          <span className="text-lg lg:text-xl font-bold text-accent-blue">{(gesture.confidence_threshold * 100).toFixed(0)}%</span>
        </div>
        <input 
          type="range" 
          min="0.1" max="1.0" step="0.05"
          value={gesture.confidence_threshold}
          onChange={(e) => onUpdate({ confidence_threshold: parseFloat(e.target.value) })}
          className="w-full accent-accent-blue h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer"
        />
        <p className="text-[10px] text-gray-500 mt-2">Adjust confidence level for better accuracy</p>
      </div>

      {/* Actions Grid */}
      <h3 className="text-xs lg:text-sm font-bold text-gray-400 uppercase mb-4">Data & Training Operations</h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 lg:gap-4">
        
        <ActionButton 
          icon={Camera} 
          label="Collect Samples" 
          sub="Use camera to add data"
          color="green"
          onClick={() => setMode('collecting')}
        />
        
        <ActionButton 
          icon={ImageIcon} 
          label="Manage Data" 
          sub="View & Edit samples"
          color="gray"
          onClick={() => setMode('gallery')}
        />

        <ActionButton 
          icon={GraduationCap} 
          label="Train This Gesture" 
          sub="Update model with new data"
          color="blue"
          onClick={() => setMode('training')}
        />

        <FileImportButton gesture={gesture} />

        <ActionButton 
          icon={Download} 
          label="Export Data" 
          sub="Download dataset as ZIP"
          color="gray"
          onClick={() => alert(`Exporting data for ${gesture.name}...`)}
        />

        <ActionButton 
          icon={Trash2} 
          label="Delete All Data" 
          sub="Remove all samples"
          color="red"
          onClick={() => confirm(`Delete all data for ${gesture.name}?`) && alert('Deleted')}
        />
      </div>
    </div>
  );
};

// --- KOMPONENTA: IMPORT PLIKÓW ---
const FileImportButton = ({ gesture }: { gesture: Gesture }) => {
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleImport = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    
    const formData = new FormData();
    Array.from(e.target.files).forEach((file) => {
      formData.append(`files`, file);
    });

    try {
      // await api.post(`/api/v1/gestures/${gesture.id}/import`, formData);
      alert(`Imported ${e.target.files.length} files for ${gesture.name}`);
    } catch {
      alert('Failed to import files');
    }
  };

  return (
    <>
      <input 
        ref={fileInputRef}
        type="file" 
        multiple 
        accept="image/*"
        className="hidden"
        onChange={handleImport}
      />
      <button
        onClick={() => fileInputRef.current?.click()}
        className="p-3 lg:p-4 rounded-xl flex flex-col items-center justify-center text-center gap-2 transition-all hover:scale-[1.02] bg-gray-700 hover:bg-gray-600 text-white h-full"
      >
        <Upload size={24} className="mb-1" />
        <div>
          <div className="font-bold text-xs lg:text-sm">Import Files</div>
          <div className="text-[9px] lg:text-[10px] opacity-70 font-normal">Upload images from disk</div>
        </div>
      </button>
    </>
  );
};

// --- TRYB: ZBIERANIE DANYCH ---
const CollectionMode = ({ gesture, onBack }: any) => {
  const [isRecording, setIsRecording] = useState(false);
  const [count, setCount] = useState(0);
  const [targetCount, setTargetCount] = useState(50);
  
  return (
    <div className="flex flex-col h-full p-4 lg:p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-4 flex-shrink-0">
        <button onClick={onBack} className="text-gray-400 hover:text-white flex items-center gap-2 font-bold text-xs lg:text-sm">
          <span className="text-lg lg:text-xl">←</span> Back to Overview
        </button>
        <h2 className="text-white font-bold flex items-center gap-2 text-sm lg:text-base">
          <Camera className="text-red-500 animate-pulse flex-shrink-0" size={20} /> Collecting: {gesture.name}
        </h2>
        <div className="px-3 py-1 bg-gray-800 rounded border border-gray-600 font-mono text-accent-blue text-xs lg:text-sm whitespace-nowrap">
          {count} / {targetCount}
        </div>
      </div>

      {/* Target Slider */}
      <div className="mb-4 bg-black/20 p-3 rounded-lg border border-gray-700 flex-shrink-0">
        <div className="flex justify-between text-xs mb-2">
          <span className="text-gray-400 font-bold">Target Samples</span>
          <span className="text-accent-blue font-bold">{targetCount}</span>
        </div>
        <input 
          type="range" 
          min="10" max="200" step="10"
          value={targetCount}
          onChange={(e) => setTargetCount(parseInt(e.target.value))}
          className="w-full accent-blue-500"
        />
      </div>

      {/* Camera Feed */}
      <div className="w-full max-w-3xl h-80 bg-black rounded-xl border border-gray-700 relative overflow-hidden flex items-center justify-center mb-4">
        <img src="http://localhost:8000/api/v1/cameras/0/stream" className="w-full h-full object-cover opacity-80" alt="Camera" />
        
        {/* Overlay */}
        <div className={`absolute inset-0 pointer-events-none flex flex-col justify-between p-4 lg:p-6 border-4 transition-colors ${
          isRecording ? 'border-red-500' : 'border-blue-500/30'
       }`}>
          <div className="flex justify-between">
            <span className={`text-xs px-2 py-1 rounded font-bold animate-pulse ${
              isRecording ? 'bg-red-600 text-white' : 'bg-gray-800 text-gray-400'
            }`}>
              {isRecording ? 'RECORDING...' : 'READY'}
            </span>
          </div>
          <div className="text-center text-white/50 text-xs lg:text-sm">
            {isRecording ? `Capturing sample ${count}...` : 'Press START to begin'}
          </div>
          <div className="text-center">
            <div className="text-3xl lg:text-4xl font-bold text-white/30">{count}</div>
            <div className="text-xs text-white/20">/ {targetCount}</div>
          </div>
        </div>
      </div>

      {/* Controls */}
      <div className="flex flex-col sm:flex-row gap-3 flex-shrink-0">
        <button 
          onClick={onBack}
          className="px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-bold text-xs lg:text-sm transition-colors flex-1"
        >
          Cancel
        </button>
        <button 
          onClick={() => { 
            if (isRecording) {
              setIsRecording(false);
            } else {
              setIsRecording(true);
              // Symulacja zbierania
              const interval = setInterval(() => {
                setCount(c => {
                  if (c >= targetCount) {
                    clearInterval(interval);
                    setIsRecording(false);
                    return c;
                  }
                  return c + 1;
                });
              }, 200);
            }
          }}
          className={`px-4 py-3 rounded-lg font-bold text-xs lg:text-sm transition-all flex-1 flex items-center justify-center gap-2 ${
            isRecording 
              ? 'bg-red-600 hover:bg-red-700 text-white' 
              : 'bg-green-600 hover:bg-green-500 text-white'
          }`}
        >
          {isRecording ? (
            <>
              <StopCircle size={16} /> STOP CAPTURE
            </>
          ) : (
            <>
              <Play size={16} /> START CAPTURE
            </>
          )}
        </button>
      </div>
    </div>
  );
};

// --- TRYB: GALERIA DANYCH ---
const GalleryMode = ({ gesture, onBack }: any) => {
  const [images, setImages] = useState<SampleImage[]>(getDemoImages(gesture.samples_count));
  const [selectedImages, setSelectedImages] = useState<number[]>([]);

  const handleDeleteImage = (id: number) => {
    setImages(prev => prev.filter(img => img.id !== id));
    setSelectedImages(prev => prev.filter(selId => selId !== id));
  };

  const handleDeleteSelected = () => {
    if (!confirm(`Delete ${selectedImages.length} images?`)) return;
    setImages(prev => prev.filter(img => !selectedImages.includes(img.id)));
    setSelectedImages([]);
  };

  const handleDeleteAll = () => {
    if (!confirm('Delete ALL images for this gesture?')) return;
    setImages([]);
    setSelectedImages([]);
  };

  const toggleImageSelection = (id: number) => {
    setSelectedImages(prev => 
      prev.includes(id) ? prev.filter(selId => selId !== id) : [...prev, id]
    );
  };

  return (
    <div className="flex flex-col h-full p-4 lg:p-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6 flex-shrink-0">
        <button onClick={onBack} className="text-gray-400 hover:text-white flex items-center gap-2 font-bold text-xs lg:text-sm">
          <span className="text-lg">←</span> Back to Overview
        </button>
        <h2 className="text-white font-bold text-sm lg:text-base">
          Manage Samples: {gesture.name} ({images.length})
        </h2>
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={handleDeleteSelected}
            disabled={selectedImages.length === 0}
            className="px-3 py-1.5 bg-orange-900/30 text-orange-400 border border-orange-500/30 rounded text-xs font-bold hover:bg-orange-900/50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Delete {selectedImages.length}
          </button>
          <button 
            onClick={handleDeleteAll}
            className="px-3 py-1.5 bg-red-900/30 text-red-400 border border-red-500/30 rounded text-xs font-bold hover:bg-red-900/50 transition-colors"
          >
            Delete All
          </button>
        </div>
      </div>

      {/* Gallery Grid */}
      <div className="flex-1 overflow-y-auto custom-scrollbar min-h-0">
        {images.length === 0 ? (
          <div className="h-full flex items-center justify-center text-gray-500">
            <div className="text-center">
              <ImageIcon size={48} className="mx-auto mb-3 opacity-20" />
              <p className="text-sm">No samples collected yet</p>
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-3 sm:grid-cols-4 md:grid-cols-5 lg:grid-cols-6 gap-2 lg:gap-3 pb-4">
            {images.map((img) => (
              <div 
                key={img.id} 
                className="relative group aspect-square"
              >
                {/* Image Container */}
                <div className={`w-full h-full rounded-lg border-2 transition-all overflow-hidden cursor-pointer ${
                  selectedImages.includes(img.id)
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-gray-700 hover:border-blue-400 bg-black/40'
                }`}>
                  <div className="w-full h-full flex items-center justify-center text-gray-600 text-[10px] bg-gradient-to-br from-gray-700 to-gray-900">
                    {img.url}
                  </div>
                </div>

                {/* Checkbox */}
                <div className="absolute top-1 left-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <input
                    type="checkbox"
                    checked={selectedImages.includes(img.id)}
                    onChange={() => toggleImageSelection(img.id)}
                    className="w-4 h-4 cursor-pointer"
                  />
                </div>

                {/* Delete Button */}
                <div className="absolute top-1 right-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <button
                    onClick={() => handleDeleteImage(img.id)}
                    className="p-1 bg-red-600 text-white rounded hover:bg-red-500 transition-colors"
                    title="Delete image"
                  >
                    <Trash2 size={12} />
                  </button>
                </div>

                {/* Selection Indicator */}
                {selectedImages.includes(img.id) && (
                  <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
                    <div className="p-2 bg-blue-500 text-white rounded-full">
                      <Check size={16} />
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

// --- TRYB: TRENOWANIE MODELU ---
const TrainingMode = ({ gesture, onBack }: any) => {
  const [progress, setProgress] = useState(0);
  const [step, setStep] = useState<'preparing' | 'training' | 'validating' | 'complete'>('preparing');

  useEffect(() => {
    // Symulacja procesu trenowania
    if (step === 'preparing') {
      setTimeout(() => {
        setProgress(33);
        setStep('training');
      }, 1000);
    } else if (step === 'training') {
      const interval = setInterval(() => {
        setProgress(p => {
          if (p >= 66) {
            clearInterval(interval);
            setStep('validating');
            return p;
          }
          return p + 1;
        });
      }, 50);
      return () => clearInterval(interval);
    } else if (step === 'validating') {
      setTimeout(() => {
        setProgress(100);
        setStep('complete');
      }, 1500);
    }
  }, [step]);

  return (
    <div className="flex flex-col h-full p-4 lg:p-8">
      
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-2xl lg:text-3xl font-bold text-white mb-2">
          Training: {gesture.name}
        </h2>
        <p className="text-gray-400 text-xs lg:text-sm">
          {step === 'preparing' && 'Preparing data and features...'}
          {step === 'training' && 'Training Random Forest model...'}
          {step === 'validating' && 'Validating model performance...'}
          {step === 'complete' && 'Training completed successfully!'}
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mb-8 bg-black/20 p-4 lg:p-6 rounded-xl border border-gray-700">
        <div className="flex justify-between items-center mb-4">
          <span className="text-sm text-gray-300 font-bold">Overall Progress</span>
          <span className="text-xl lg:text-2xl font-bold text-accent-blue">{progress}%</span>
        </div>
        <div className="w-full bg-gray-800 h-3 rounded-full overflow-hidden">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-accent-blue transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
      </div>

      {/* Steps */}
      <div className="space-y-3 mb-8 flex-1">
        <TrainingStep 
          label="Data Preparation"
          status={step === 'complete' || step === 'training' || step === 'validating' ? 'complete' : step === 'preparing' ? 'active' : 'pending'}
        />
        <TrainingStep 
          label="Model Training (100 trees)"
          status={step === 'complete' || step === 'validating' ? 'complete' : step === 'training' ? 'active' : 'pending'}
        />
        <TrainingStep 
          label="Cross-Validation"
          status={step === 'complete' ? 'complete' : step === 'validating' ? 'active' : 'pending'}
        />
      </div>

      {/* Results */}
      {step === 'complete' && (
        <div className="mb-8 bg-green-500/10 border border-green-500/30 rounded-xl p-4 lg:p-6">
          <h3 className="text-lg font-bold text-green-400 mb-4 flex items-center gap-2">
            <Check size={20} /> Training Results
          </h3>
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 text-xs lg:text-sm">
            <div>
              <span className="text-gray-400 block">Accuracy</span>
              <span className="text-green-400 font-bold text-lg">96.5%</span>
            </div>
            <div>
              <span className="text-gray-400 block">Precision</span>
              <span className="text-green-400 font-bold text-lg">97.2%</span>
            </div>
            <div>
              <span className="text-gray-400 block">Recall</span>
              <span className="text-green-400 font-bold text-lg">95.8%</span>
            </div>
            <div>
              <span className="text-gray-400 block">F1-Score</span>
              <span className="text-green-400 font-bold text-lg">96.5%</span>
            </div>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex flex-col sm:flex-row gap-3 flex-shrink-0">
        <button 
          onClick={onBack}
          disabled={step !== 'complete'}
          className="px-4 py-3 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 text-white rounded-lg font-bold text-xs lg:text-sm transition-colors flex-1 disabled:cursor-not-allowed"
        >
          {step === 'complete' ? 'Return to Overview' : 'Training in progress...'}
        </button>
        {step === 'complete' && (
          <button 
            onClick={() => alert('Model saved and deployed!')}
            className="px-4 py-3 bg-green-600 hover:bg-green-500 text-white rounded-lg font-bold text-xs lg:text-sm transition-colors flex-1"
          >
            Deploy Model
          </button>
        )}
      </div>
    </div>
  );
};

// --- KOMPONENTY POMOCNICZE ---

const GestureListItem = ({ gesture, isSelected, onClick }: any) => (
  <div
    onClick={onClick}
    className={`p-3 rounded-lg cursor-pointer transition-all border flex justify-between items-center min-w-0 ${
      isSelected ? 'bg-blue-500/10 border-blue-500/50' : 'bg-gray-800/40 border-transparent hover:bg-gray-700'
    }`}
  >
    <div className="flex items-center gap-3 min-w-0 flex-1">
      <span className="text-lg lg:text-xl flex-shrink-0">{gesture.description?.split(' ')[0] || '✋'}</span>
      <div className="min-w-0 flex-1">
        <p className={`text-xs lg:text-sm font-bold truncate ${isSelected ? 'text-white' : 'text-gray-300'}`}>
          {gesture.name}
        </p>
        <p className="text-[9px] text-gray-500 truncate uppercase">{gesture.samples_count} samples</p>
      </div>
    </div>
    <div className={`w-2 h-2 rounded-full flex-shrink-0 ${gesture.trained ? 'bg-green-500' : 'bg-red-500'}`} />
  </div>
);

const ActionButton = ({ icon: Icon, label, sub, color, onClick }: any) => {
  const colorClasses: any = {
    blue: 'bg-blue-600 hover:bg-blue-500 text-white',
    green: 'bg-green-600 hover:bg-green-500 text-white',
    red: 'bg-red-900/20 border border-red-500/30 text-red-400 hover:bg-red-900/40',
    gray: 'bg-gray-700 hover:bg-gray-600 text-white',
  };

  return (
    <button 
      onClick={onClick}
      className={`p-3 lg:p-4 rounded-xl flex flex-col items-center justify-center text-center gap-2 transition-all hover:scale-[1.02] ${colorClasses[color]} h-full`}
    >
      <Icon size={24} className="mb-1 flex-shrink-0" />
      <div className="min-w-0">
        <div className="font-bold text-xs lg:text-sm">{label}</div>
        {sub && <div className="text-[9px] lg:text-[10px] opacity-70 font-normal">{sub}</div>}
      </div>
    </button>
  );
};

const StatBox = ({ label, value, icon: Icon, color }: any) => (
  <div className="bg-black/20 p-3 lg:p-4 rounded-xl border border-gray-700 flex items-center gap-3">
    <div className={`p-2 rounded-lg bg-${color}-500/10 text-${color}-400 flex-shrink-0`}>
      <Icon size={18} />
    </div>
    <div className="min-w-0 flex-1">
      <div className="text-lg lg:text-xl font-bold text-white leading-none truncate">{value}</div>
      <div className="text-[9px] lg:text-[10px] text-gray-500 uppercase font-bold mt-1">{label}</div>
    </div>
  </div>
);

const TrainingStep = ({ label, status }: { label: string, status: 'pending' | 'active' | 'complete' }) => {
  const icons = {
    pending: <div className="w-5 h-5 rounded-full border-2 border-gray-600" />,
    active: <Loader size={20} className="text-accent-blue animate-spin" />,
    complete: <Check size={20} className="text-green-500" />
  };
  
  const colors = {
    pending: 'text-gray-500',
    active: 'text-white font-bold',
    complete: 'text-gray-300'
  };

  return (
    <div className="flex items-center gap-4 p-4 bg-black/20 rounded-lg border border-gray-800">
      {icons[status]}
      <span className={`text-sm ${colors[status]}`}>{label}</span>
    </div>
  );
};

// --- MODAL DODAWANIA GESTU ---
const AddGestureModal = ({ onClose, onAdded }: any) => {
  const [formData, setFormData] = useState({
    name: '',
    emoji: '✋',
    category: 'static',
    machine_action: '',
    description: ''
  });

  const emojiOptions = ['✋', '✊', '👉', '👌', '☝️', '✌️', '🤙', '🖐️'];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      alert(`Gesture "${formData.name}" created successfully!`);
      onAdded();
      onClose();
    } catch {
      alert('Failed to create gesture');
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-industrial-gray rounded-xl border border-gray-700 p-6 w-full max-w-md max-h-[90vh] overflow-y-auto shadow-2xl custom-scrollbar">
        <div className="flex justify-between items-center mb-6 sticky top-0 bg-industrial-gray z-10 pb-4">
          <h3 className="text-lg lg:text-xl font-bold text-white flex items-center gap-2">
            <Plus className="text-blue-400" size={20} />
            Create New Gesture
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-white transition-colors flex-shrink-0">
            <X size={20} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs lg:text-sm text-gray-400 mb-2">Gesture Name</label>
            <input 
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({...formData, name: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="e.g., thumbs_up"
              pattern="[A-Za-z_]+"
              required
            />
            <p className="text-[10px] text-gray-500 mt-1">Use only A-Z and underscores</p>
          </div>

          <div>
            <label className="block text-xs lg:text-sm text-gray-400 mb-2">Select Emoji</label>
            <div className="flex gap-1 mb-2 flex-wrap">
              {emojiOptions.map((emoji) => (
                <button
                  key={emoji}
                  type="button"
                  onClick={() => setFormData({...formData, emoji})}
                  className={`text-2xl p-2 rounded-lg border-2 transition-all ${
                    formData.emoji === emoji ? 'border-blue-500 bg-blue-500/10' : 'border-gray-700 hover:border-gray-600'
                  }`}
                >
                  {emoji}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs lg:text-sm text-gray-400 mb-2">Category</label>
            <select
              value={formData.category}
              onChange={(e) => setFormData({...formData, category: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="static">Static</option>
              <option value="dynamic">Dynamic</option>
            </select>
          </div>

          <div>
            <label className="block text-xs lg:text-sm text-gray-400 mb-2">Machine Action</label>
            <input 
              type="text"
              value={formData.machine_action}
              onChange={(e) => setFormData({...formData, machine_action: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="e.g., START_PROCESS"
              required
            />
          </div>

          <div>
            <label className="block text-xs lg:text-sm text-gray-400 mb-2">Description</label>
            <textarea 
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500 h-16"
              placeholder="Brief description of the gesture"
            />
          </div>

          <div className="flex gap-3 pt-4 sticky bottom-0 bg-industrial-gray pb-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg font-bold text-sm transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg font-bold text-sm transition-colors"
            >
              Create
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// --- MOCK DATA ---
const getDemoGestures = (): Gesture[] => [
  { id: 1, name: 'Fist', category: 'Static', description: '✊ Stop', machine_action: 'STOP', is_default: true, enabled: true, confidence_threshold: 0.8, samples_count: 150, trained: true, accuracy: 98, detections: 1200 },
  { id: 2, name: 'Open Hand', category: 'Static', description: '✋ Start', machine_action: 'START', is_default: true, enabled: true, confidence_threshold: 0.8, samples_count: 120, trained: true, accuracy: 95, detections: 800 },
  { id: 3, name: 'Peace', category: 'Static', description: '✌️ Mode 2', machine_action: 'MODE_2', is_default: false, enabled: false, confidence_threshold: 0.75, samples_count: 40, trained: false, accuracy: 0, detections: 0 },
  { id: 4, name: 'Thumbs Up', category: 'Static', description: '👍 Confirm', machine_action: 'CONFIRM', is_default: false, enabled: true, confidence_threshold: 0.7, samples_count: 80, trained: false, accuracy: 0, detections: 0 },
];

const getDemoImages = (count: number): SampleImage[] => 
  Array.from({length: count}).map((_, i) => ({
    id: i,
    url: `sample_${i + 1}.jpg`,
    timestamp: new Date(Date.now() - i * 60000).toISOString()
  }));

export default Training;
