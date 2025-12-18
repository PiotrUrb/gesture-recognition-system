// ZMIANA #2: frontend/src/pages/Cameras.tsx
// Suwaki 0-200 + nowe parametry
// Auto-detection WebSocket

import { useState, useEffect } from 'react';
import { Camera, Plus, Trash2, Save, RotateCcw } from 'lucide-react';
import api from '../services/api';

interface CameraDevice {
  id: number;
  name?: string;
  source: string;
  type: string;
  fps: number;
  width: number;
  height: number;
  actual_width?: number;
  actual_height?: number;
  actual_fps?: number;
}

interface CameraResponse {
  status: string;
  camera_id?: number;
  message?: string;
}

interface CameraSettings {
  brightness: number;
  contrast: number;
  saturation: number;
  gamma: number;
  hue: number;
  blur: number;
  exposure: number;
}

const Cameras = () => {
  const [cameras, setCameras] = useState<CameraDevice[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<CameraDevice | null>(null);
  const [settings, setSettings] = useState<CameraSettings>({
    brightness: 100,
    contrast: 100,
    saturation: 100,
    gamma: 100,
    hue: 0,
    blur: 0,
    exposure: 100
  });
  const [showAddModal, setShowAddModal] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [saveMessage, setSaveMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadCameras();
  }, []);

  const loadCameras = async (): Promise<void> => {
    try {
      setIsLoading(true);
      const res = await api.get<{ cameras: CameraDevice[] }>('/api/v1/cameras/');
      const backendCameras = res.data.cameras || [];
      
      setCameras(backendCameras);
      if (backendCameras.length > 0 && !selectedCamera) {
        setSelectedCamera(backendCameras[0]);
      }
    } catch (error) {
      console.error('Error loading cameras:', error);
      setSaveMessage({ type: 'error', text: 'Failed to load cameras' });
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSettings = (): void => {
    setSettings({
      brightness: 100,
      contrast: 100,
      saturation: 100,
      gamma: 100,
      hue: 0,
      blur: 0,
      exposure: 100
    });
  };

  const handleRemoveCamera = async (): Promise<void> => {
    if (!selectedCamera) return;
    if (!window.confirm(`Remove ${selectedCamera.source}?`)) return;

    try {
      await api.delete(`/api/v1/cameras/${selectedCamera.id}`);
      
      const newCameras = cameras.filter(c => c.id !== selectedCamera.id);
      setCameras(newCameras);

      if (newCameras.length > 0) {
        setSelectedCamera(newCameras[0]);
      } else {
        setSelectedCamera(null);
      }

      setSaveMessage({ type: 'success', text: 'Camera removed!' });
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      console.error('Error removing camera:', error);
      setSaveMessage({ type: 'error', text: 'Failed to remove camera' });
    }
  };

  const handleSaveSettings = async (): Promise<void> => {
    if (!selectedCamera) return;

    try {
      await api.post(`/api/v1/cameras/${selectedCamera.id}/settings`, settings);

      setSaveMessage({ 
        type: 'success', 
        text: 'Settings saved!' 
      });
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setSaveMessage({ type: 'error', text: 'Failed to save settings' });
    }
  };

  const handleAddCamera = async (newCam: NewCamera): Promise<void> => {
    try {
      await api.post<CameraResponse>('/api/v1/cameras/', {
        source: newCam.source,
        camera_type: newCam.type,
        name: newCam.name
      });

      await loadCameras();
      setShowAddModal(false);

      setSaveMessage({ type: 'success', text: 'Camera added!' });
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (error) {
      console.error('Error adding camera:', error);
      setSaveMessage({ type: 'error', text: 'Failed to add camera' });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-center">
          <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-400">Loading cameras...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col lg:flex-row gap-4 p-4 lg:p-6 overflow-hidden bg-gray-900">
      {/* LEFT PANEL - CAMERA LIST */}
      <div className="w-full lg:w-64 flex flex-col gap-3 bg-gray-800 rounded-xl border border-gray-700 p-4 overflow-hidden">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-lg font-bold text-white flex items-center gap-2">
            <Camera size={20} className="text-blue-500" />
            Cameras
          </h2>
          <button
            onClick={() => setShowAddModal(true)}
            className="p-1.5 bg-blue-600 hover:bg-blue-500 rounded text-white transition-colors"
            title="Add camera"
          >
            <Plus size={16} />
          </button>
        </div>

        {saveMessage && (
          <div
            className={`p-2 rounded text-xs font-bold ${
              saveMessage.type === 'success'
                ? 'bg-green-900 border border-green-700 text-green-400'
                : 'bg-red-900 border border-red-700 text-red-400'
            }`}
          >
            {saveMessage.text}
          </div>
        )}

        <div className="flex-1 overflow-y-auto space-y-2">
          {cameras.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <p className="text-sm">No cameras</p>
              <p className="text-xs opacity-75">Add one to get started</p>
            </div>
          ) : (
            cameras.map(cam => (
              <button
                key={cam.id}
                onClick={() => setSelectedCamera(cam)}
                className={`w-full p-3 rounded-lg text-left transition-all border text-xs ${
                  selectedCamera?.id === cam.id
                    ? 'bg-blue-500/10 border-blue-500/50'
                    : 'bg-gray-700 border-transparent hover:bg-gray-600'
                }`}
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-white">{cam.name || `Camera ${cam.id}`}</span>
                  <span className="w-2 h-2 rounded-full bg-green-500" />
                </div>
                <div className="text-gray-400 space-y-0.5">
                  <div>{cam.width}×{cam.height} • {cam.fps}fps</div>
                  <div className="text-gray-500">{cam.type.toUpperCase()}</div>
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* RIGHT PANEL - CAMERA EDITOR */}
      <div className="flex-1 flex flex-col gap-4 overflow-hidden">
        {selectedCamera ? (
          <>
            {/* Preview - MJPEG STREAM */}
            <div className="bg-gray-800 rounded-xl border border-gray-700 p-4 h-64 lg:h-80 flex items-center justify-center overflow-hidden">
              <img
                key={selectedCamera.id}
                src={`http://localhost:8000/api/v1/cameras/${selectedCamera.id}/stream?quality=medium`}
                alt="Camera Preview"
                className="w-full h-full object-cover rounded"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                  const parent = e.currentTarget.parentElement;
                  if (parent && !parent.querySelector('.error-msg')) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'error-msg text-gray-500 text-center';
                    errorDiv.innerHTML = 'Stream unavailable';
                    parent.appendChild(errorDiv);
                  }
                }}
              />
            </div>

            {/* Settings */}
            <div className="flex-1 bg-gray-800 rounded-xl border border-gray-700 p-4 overflow-y-auto space-y-4">
              <div>
                <h3 className="text-sm font-bold text-white mb-4">Image Adjustments (0-200 scale)</h3>
                <div className="space-y-4">
                  
                  {/* BRIGHTNESS: 0-200 */}
                  <SliderControl
                    label="Brightness"
                    value={settings.brightness}
                    min={0}
                    max={200}
                    center={100}
                    unit="%"
                    onChange={(val) => setSettings({ ...settings, brightness: val })}
                    tooltip="0=very dark, 100=normal, 200=very bright"
                  />

                  {/* CONTRAST: 0-200 */}
                  <SliderControl
                    label="Contrast"
                    value={settings.contrast}
                    min={0}
                    max={200}
                    center={100}
                    unit="%"
                    onChange={(val) => setSettings({ ...settings, contrast: val })}
                    tooltip="0=flat, 100=normal, 200=high"
                  />

                  {/* SATURATION: 0-200 */}
                  <SliderControl
                    label="Saturation"
                    value={settings.saturation}
                    min={0}
                    max={200}
                    center={100}
                    unit="%"
                    onChange={(val) => setSettings({ ...settings, saturation: val })}
                    tooltip="0=grayscale, 100=normal, 200=super saturated"
                  />

                  {/* GAMMA: 0-200 */}
                  <SliderControl
                    label="Gamma"
                    value={settings.gamma}
                    min={0}
                    max={200}
                    center={100}
                    unit="%"
                    onChange={(val) => setSettings({ ...settings, gamma: val })}
                    tooltip="0=very dark, 100=normal, 200=very bright"
                  />

                  {/* HUE: -180 to 180 */}
                  <SliderControl
                    label="Hue"
                    value={settings.hue}
                    min={-180}
                    max={180}
                    center={0}
                    unit="°"
                    onChange={(val) => setSettings({ ...settings, hue: val })}
                    tooltip="Color shift: -180=invert, 0=none, 180=invert"
                  />

                  {/* BLUR: 0-50 */}
                  <SliderControl
                    label="Blur"
                    value={settings.blur}
                    min={0}
                    max={50}
                    center={0}
                    unit=""
                    onChange={(val) => setSettings({ ...settings, blur: val })}
                    tooltip="Smoothing effect (0=none, 50=max)"
                  />

                  {/* EXPOSURE: 0-200 */}
                  <SliderControl
                    label="Exposure"
                    value={settings.exposure}
                    min={0}
                    max={200}
                    center={100}
                    unit="%"
                    onChange={(val) => setSettings({ ...settings, exposure: val })}
                    tooltip="0=very dark, 100=normal, 200=very bright"
                  />
                </div>
              </div>

              <div className="border-t border-gray-700 pt-4">
                <h3 className="text-sm font-bold text-white mb-3">Camera Information</h3>
                <div className="space-y-2 text-sm text-gray-400">
                  <InfoRow label="ID" value={selectedCamera.id.toString()} />
                  <InfoRow label="Source" value={selectedCamera.source} />
                  <InfoRow label="Type" value={selectedCamera.type.toUpperCase()} />
                  <InfoRow label="Resolution" value={`${selectedCamera.width}×${selectedCamera.height}`} />
                  <InfoRow label="FPS" value={selectedCamera.fps.toString()} />
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-2 pt-4 border-t border-gray-700">
                <button
                  onClick={handleResetSettings}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  <RotateCcw size={14} />
                  Reset
                </button>
                <button
                  onClick={handleRemoveCamera}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-red-600 hover:bg-red-500 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  <Trash2 size={14} />
                  Remove
                </button>
                <button
                  onClick={handleSaveSettings}
                  className="flex-1 flex items-center justify-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-xs font-bold transition-colors"
                >
                  <Save size={14} />
                  Save
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 bg-gray-800 rounded-xl border border-gray-700 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <Camera size={48} className="mx-auto mb-2 opacity-50" />
              <p className="text-sm">Select a camera to configure</p>
            </div>
          </div>
        )}
      </div>

      {showAddModal && (
        <AddCameraModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddCamera}
        />
      )}
    </div>
  );
};

/* SLIDER CONTROL COMPONENT */
interface SliderControlProps {
  label: string;
  value: number;
  min: number;
  max: number;
  center?: number;
  unit: string;
  onChange: (value: number) => void;
  tooltip?: string;
}

const SliderControl: React.FC<SliderControlProps> = ({
  label,
  value,
  min,
  max,
  center = min,
  unit,
  onChange,
  tooltip
}) => {
  // Calculate color based on center point
  let sliderColor = 'accent-blue-500';
  if (center !== undefined && value < center) {
    sliderColor = 'accent-blue-500';
  } else if (center !== undefined && value > center) {
    sliderColor = 'accent-orange-500';
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <label className="text-xs text-gray-400 font-bold">{label}</label>
        <div className="flex items-center gap-2">
          <span className="text-sm text-blue-400 font-bold w-12 text-right">
            {value}{unit}
          </span>
          {center !== undefined && value === center && (
            <span className="text-xs text-green-400 font-bold">DEFAULT</span>
          )}
        </div>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        value={value}
        onChange={(e) => onChange(parseInt(e.target.value))}
        className={`w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer ${sliderColor}`}
        title={tooltip}
      />
      <div className="flex justify-between text-xs text-gray-500 mt-1 px-1">
        <span>{min}</span>
        {center !== undefined && <span>{center}</span>}
        <span>{max}</span>
      </div>
    </div>
  );
};

/* INFO ROW COMPONENT */
interface InfoRowProps {
  label: string;
  value: string;
}

const InfoRow: React.FC<InfoRowProps> = ({ label, value }) => (
  <div className="flex justify-between items-center py-1">
    <span className="text-gray-500">{label}:</span>
    <span className="text-white font-mono">{value}</span>
  </div>
);

/* ADD CAMERA MODAL */
interface NewCamera {
  name: string;
  source: string;
  type: string;
}

interface AddCameraModalProps {
  onClose: () => void;
  onAdd: (cam: NewCamera) => Promise<void>;
}

const AddCameraModal: React.FC<AddCameraModalProps> = ({ onClose, onAdd }) => {
  const [formData, setFormData] = useState<NewCamera>({ name: '', source: '', type: 'usb' });

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>): Promise<void> => {
    e.preventDefault();
    if (!formData.name || !formData.source) {
      alert('Please fill all fields');
      return;
    }
    await onAdd(formData);
    setFormData({ name: '', source: '', type: 'usb' });
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-gray-800 border border-gray-700 rounded-xl p-6 max-w-md w-full mx-4">
        <h2 className="text-lg font-bold text-white mb-4">Add New Camera</h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs text-gray-400 mb-2 uppercase font-bold">Camera Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder="e.g., Main Camera"
            />
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-2 uppercase font-bold">Camera Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
            >
              <option value="usb">USB Camera</option>
              <option value="ip">IP Camera (RTSP)</option>
              <option value="file">Video File</option>
            </select>
          </div>

          <div>
            <label className="block text-xs text-gray-400 mb-2 uppercase font-bold">
              Source {formData.type === 'usb' ? '(Index)' : formData.type === 'ip' ? '(RTSP URL)' : '(File Path)'}
            </label>
            <input
              type="text"
              value={formData.source}
              onChange={(e) => setFormData({ ...formData, source: e.target.value })}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-white text-sm focus:outline-none focus:border-blue-500"
              placeholder={
                formData.type === 'usb'
                  ? '0'
                  : formData.type === 'ip'
                  ? 'rtsp://192.168.1.100:554/stream'
                  : '/path/to/video.mp4'
              }
            />
          </div>

          <div className="flex gap-2 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-3 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-bold transition-colors flex items-center justify-center gap-2"
            >
              <Plus size={14} />
              Add
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Cameras;