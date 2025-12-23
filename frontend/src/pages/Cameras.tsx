import { useEffect, useState } from 'react';
import {
  Camera,
  Plus,
  Trash2,
  Save,
  Sliders,
  Monitor,
  Wifi,
  RotateCcw
} from 'lucide-react';
import api from '../services/api';

/* ===================== TYPES ===================== */

interface CameraDevice {
  id: number;
  name?: string;
  source: string;
  type: 'usb' | 'ip' | 'file';
  fps: number;
  width: number;
  height: number;
  is_active?: boolean;
}

interface CameraSettings {
  brightness: number;
  contrast: number;
  saturation: number;
  exposure: number;
}

interface NewCamera {
  name: string;
  source: string;
  type: string;
}

/* ===================== MAIN ===================== */

const Cameras = () => {
  const [cameras, setCameras] = useState<CameraDevice[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<CameraDevice | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);

  const [settings, setSettings] = useState<CameraSettings>({
    brightness: 100,
    contrast: 100,
    saturation: 100,
    exposure: 100
  });

  const loadCameras = async () => {
    const res = await api.get<{ cameras: CameraDevice[] }>('/api/v1/cameras/');
    const cams = res.data.cameras ?? [];
    setCameras(cams);
    if (cams.length && !selectedCamera) setSelectedCamera(cams[0]);
  };

  useEffect(() => {
    loadCameras();
  }, []);

  const handleSaveSettings = async () => {
    if (!selectedCamera) return;
    await api.post(
      `/api/v1/cameras/${selectedCamera.id}/settings`,
      settings
    );
  };

  const handleResetSettings = () =>
    setSettings({
      brightness: 100,
      contrast: 100,
      saturation: 100,
      exposure: 100
    });

  const handleRemoveCamera = async () => {
    if (!selectedCamera) return;
    if (!confirm('Remove this camera?')) return;
    await api.delete(`/api/v1/cameras/${selectedCamera.id}`);
    setSelectedCamera(null);
    await loadCameras();
  };

const handleAddCamera = async (cam: NewCamera) => {
    await api.post('/api/v1/cameras/', {
        name: cam.name,
        source: cam.source,
        type: cam.type
    });
    await loadCameras();
};

  return (
    <div className="min-h-screen p-4 flex flex-col xl:flex-row gap-6">

      {/* LEFT PANEL */}
      <div className="xl:w-80 w-full bg-industrial-gray rounded-xl border border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700 flex justify-between items-center">
          <h3 className="font-bold flex items-center gap-2">
            <Camera size={18} /> Cameras
          </h3>
          <button
            onClick={() => setShowAddModal(true)}
            className="p-2 bg-blue-600 rounded hover:bg-blue-500"
          >
            <Plus size={16} />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-2 space-y-2">
          {cameras.map(cam => (
            <button
              key={cam.id}
              onClick={() => setSelectedCamera(cam)}
              className={`w-full text-left p-3 rounded-lg border transition ${
                selectedCamera?.id === cam.id
                  ? 'bg-blue-500/10 border-blue-500/50'
                  : 'bg-gray-800/50 hover:bg-gray-700'
              }`}
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-2">
                  {cam.type === 'usb'
                    ? <Monitor size={14} />
                    : <Wifi size={14} />}
                  <span className="font-bold text-sm text-gray-100">
                    {cam.name || `Camera ${cam.id}`}
                  </span>
                </div>
                <span
                  className={`w-2 h-2 rounded-full ${
                    cam.is_active ? 'bg-green-500' : 'bg-red-500'
                  }`}
                />
              </div>
              <p className="text-xs text-gray-400 truncate mt-1">
                {cam.source}
              </p>
            </button>
          ))}
        </div>
      </div>

      {/* RIGHT PANEL */}
      <div className="flex-1 flex flex-col gap-6">

        {selectedCamera ? (
          <>
            {/* PREVIEW */}
            <div className="bg-black rounded-xl border border-gray-700 aspect-video flex items-center justify-center">
              <img
                src={`http://localhost:8000/api/v1/cameras/${selectedCamera.id}/stream`}
                className="max-h-full max-w-full object-contain"
              />
            </div>

            {/* CAMERA INFO */}
            <div className="bg-industrial-gray border border-gray-700 rounded-xl p-4 grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <Info label="Name" value={selectedCamera.name || '—'} />
              <Info label="Type" value={selectedCamera.type.toUpperCase()} />
              <Info label="FPS" value={selectedCamera.fps} />
              <Info
                label="Resolution"
                value={`${selectedCamera.width}×${selectedCamera.height}`}
              />
              <div className="col-span-2 md:col-span-4">
                <Info label="Source" value={selectedCamera.source} />
              </div>
            </div>

            {/* SETTINGS */}
            <div className="bg-industrial-gray rounded-xl border border-gray-700 p-4 md:p-6 flex flex-col gap-4">
              <div className="flex flex-wrap justify-between gap-3">
                <h3 className="font-bold flex items-center gap-2">
                  <Sliders size={16} /> Image Adjustment
                </h3>
                <div className="flex gap-2">
                  <button onClick={handleResetSettings} className="btn-secondary">
                    <RotateCcw size={14} />
                  </button>
                  <button onClick={handleRemoveCamera} className="btn-danger">
                    <Trash2 size={14} />
                  </button>
                  <button onClick={handleSaveSettings} className="btn-primary">
                    <Save size={14} />
                  </button>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6">
                <Slider
                  label="Brightness"
                  value={settings.brightness}
                  onChange={v => setSettings({ ...settings, brightness: v })}
                />
                <Slider
                  label="Contrast"
                  value={settings.contrast}
                  onChange={v => setSettings({ ...settings, contrast: v })}
                />
                <Slider
                  label="Saturation"
                  value={settings.saturation}
                  onChange={v => setSettings({ ...settings, saturation: v })}
                />
                <Slider
                  label="Exposure"
                  value={settings.exposure}
                  onChange={v => setSettings({ ...settings, exposure: v })}
                />
              </div>
            </div>
          </>
        ) : (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            Select a camera
          </div>
        )}
      </div>

      {showAddModal && (
        <AddCameraModal
          onClose={() => setShowAddModal(false)}
          onAdd={async cam => {
            await handleAddCamera(cam);
            setShowAddModal(false);
          }}
        />
      )}
    </div>
  );
};

/* ===================== COMPONENTS ===================== */

const Info = ({ label, value }: { label: string; value: any }) => (
  <div>
    <p className="text-xs text-gray-400 font-bold">{label}</p>
    <p className="text-gray-100 break-all">{value}</p>
  </div>
);

const Slider = ({
  label,
  value,
  onChange
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
}) => (
  <div>
    <div className="flex justify-between text-sm mb-1 text-gray-300">
      <span>{label}</span>
      <span className="font-mono">{value}</span>
    </div>
    <input
      type="range"
      min={0}
      max={200}
      value={value}
      onChange={e => onChange(+e.target.value)}
      className="w-full accent-blue-500"
    />
  </div>
);

/* ===================== ADD CAMERA MODAL ===================== */

const AddCameraModal = ({
  onClose,
  onAdd
}: {
  onClose: () => void;
  onAdd: (cam: NewCamera) => Promise<void>;
}) => {
  const [form, setForm] = useState<NewCamera>({
    name: '',
    source: '',
    type: 'usb'
  });

  const inputClass =
    'w-full rounded bg-gray-800 border border-gray-600 px-3 py-2 ' +
    'text-gray-100 placeholder-gray-400 focus:outline-none ' +
    'focus:ring-2 focus:ring-blue-500';

  return (
    <div className="fixed inset-0 bg-black/70 backdrop-blur flex items-center justify-center z-50 p-4">
      <div className="bg-industrial-gray border border-gray-700 rounded-xl w-full max-w-lg p-6 space-y-5">

        <h2 className="text-lg font-bold flex items-center gap-2">
          <Camera size={18} /> Add Camera
        </h2>

        <div className="grid gap-4">
          <div>
            <label className="text-xs text-gray-400 font-bold">NAME</label>
            <input
              className={inputClass}
              value={form.name}
              onChange={e => setForm({ ...form, name: e.target.value })}
            />
          </div>

          <div>
            <label className="text-xs text-gray-400 font-bold">TYPE</label>
            <select
              className={inputClass}
              value={form.type}
              onChange={e => setForm({ ...form, type: e.target.value })}
            >
              <option value="usb">USB Camera</option>
              <option value="ip">IP Camera (RTSP)</option>
              <option value="file">Video File</option>
            </select>
          </div>

          <div>
            <label className="text-xs text-gray-400 font-bold">SOURCE</label>
            <input
              className={inputClass}
              value={form.source}
              placeholder={
                form.type === 'usb'
                  ? '0'
                  : form.type === 'ip'
                  ? 'rtsp://192.168.1.100:554/stream'
                  : '/videos/file.mp4'
              }
              onChange={e => setForm({ ...form, source: e.target.value })}
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 pt-4">
          <button onClick={onClose} className="btn-secondary flex-1">
            Cancel
          </button>
          <button onClick={() => onAdd(form)} className="btn-primary flex-1">
            Add Camera
          </button>
        </div>
      </div>
    </div>
  );
};

export default Cameras;
