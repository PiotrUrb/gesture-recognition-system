/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from 'react';
import { 
  Settings as SettingsIcon,
  Sliders,
  HardDrive,
  Download,
  Upload,
  RotateCcw,
  Save,
  Brain,
  AlertTriangle,
  Check,
  Info
} from 'lucide-react';
import api from '../services/api';

interface SystemSettings {
  detection: {
    confidence_threshold: number;
    cooldown_ms: number;
    multi_hand_enabled: boolean;
  };
  model: {
    algorithm: string;
    auto_retrain: boolean;
  };
  system: {
    auto_start_cameras: boolean;
    gpu_acceleration: boolean;
    sound_alerts: boolean;
  };
}

const Settings = () => {
  const [settings, setSettings] = useState<SystemSettings>({
    detection: {
      confidence_threshold: 0.75,
      cooldown_ms: 500,
      multi_hand_enabled: false,
    },
    model: {
      algorithm: 'RandomForest',
      auto_retrain: false,
    },
    system: {
      auto_start_cameras: true,
      gpu_acceleration: true,
      sound_alerts: true,
    }
  });

  const [systemInfo, setSystemInfo] = useState<any>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState<{type: 'success' | 'error', text: string} | null>(null);

  useEffect(() => {
    // Mock load settings
    loadSystemInfo();
  }, []);

  const loadSystemInfo = async () => {
    try {
      const res = await api.get('/api/v1/system/info');
      setSystemInfo(res.data);
    } catch (e) {
      console.error('Failed to load system info', e);
      setSystemInfo({
        cpu_usage: 23.5,
        ram_usage: 42.1,
        disk_space: 67.8,
        model_version: 'v1.2.3'
      });
    }
  };

  const handleSave = async () => {
    setIsSaving(true);
    setSaveMessage(null);
    try {
      await api.post('/api/v1/settings', settings);
      setSaveMessage({ type: 'success', text: 'Settings saved successfully!' });
      setTimeout(() => setSaveMessage(null), 3000);
    } catch (e) {
      console.error('Failed to save settings', e);
      setSaveMessage({ type: 'error', text: 'Failed to save settings.' });
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col gap-6">
      
      {/* HEADER */}
      <div className="bg-industrial-gray rounded-xl border border-gray-700 p-6 shadow-lg flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold text-white flex items-center gap-3 mb-2">
            <SettingsIcon className="text-accent-blue" size={28} />
            System Settings
          </h1>
          <p className="text-gray-400 text-sm">Core configuration and system status</p>
        </div>

        <div className="flex gap-2">
          <button 
            onClick={() => {
              if(confirm('Reset to defaults?')) window.location.reload();
            }}
            className="px-4 py-2 bg-red-600/20 hover:bg-red-600/30 text-red-400 border border-red-500/30 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
          >
            <RotateCcw size={16} />
            Reset
          </button>
          <button 
            onClick={handleSave}
            disabled={isSaving}
            className="px-6 py-2 bg-accent-blue hover:bg-blue-500 disabled:bg-gray-600 text-white rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
          >
            <Save size={16} />
            {isSaving ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      {/* ALERT MESSAGE */}
      {saveMessage && (
        <div className={`p-3 rounded-lg flex items-center gap-2 ${
          saveMessage.type === 'success' 
            ? 'bg-green-500/20 border border-green-500/30 text-green-400' 
            : 'bg-red-500/20 border border-red-500/30 text-red-400'
        }`}>
          {saveMessage.type === 'success' ? <Check size={16} /> : <AlertTriangle size={16} />}
          <span className="text-sm font-medium">{saveMessage.text}</span>
        </div>
      )}

      {/* CONTENT GRID */}
      <div className="flex-1 grid grid-cols-2 gap-6 overflow-y-auto custom-scrollbar pb-6">
        
        {/* LEFT COLUMN */}
        <div className="space-y-6">
          
          {/* DETECTION SETTINGS (Kluczowe) */}
          <SettingsSection icon={<Sliders className="text-blue-400" size={20} />} title="Detection Parameters">
            <SettingSlider 
              label="Sensitivity (Threshold)"
              value={settings.detection.confidence_threshold}
              onChange={(v: number) => setSettings({...settings, detection: {...settings.detection, confidence_threshold: v}})}
              min={0.5}
              max={0.95}
              step={0.05}
              unit="%"
              multiplier={100}
              description="Minimum confidence required to trigger action"
            />
            <SettingSlider 
              label="Detection Cooldown"
              value={settings.detection.cooldown_ms}
              onChange={(v: number) => setSettings({...settings, detection: {...settings.detection, cooldown_ms: v}})}
              min={100}
              max={2000}
              step={100}
              unit="ms"
              description="Wait time between consecutive gestures"
            />
            <SettingToggle 
              label="Multi-Hand Mode"
              value={settings.detection.multi_hand_enabled}
              onChange={(v: boolean) => setSettings({...settings, detection: {...settings.detection, multi_hand_enabled: v}})}
              description="Enable detection for both hands simultaneously"
            />
          </SettingsSection>

          {/* MODEL CONFIGURATION (Kluczowe) */}
          <SettingsSection icon={<Brain className="text-purple-400" size={20} />} title="Model Configuration">
            <SettingSelect 
              label="Classification Algorithm"
              value={settings.model.algorithm}
              onChange={(v: string) => setSettings({...settings, model: {...settings.model, algorithm: v}})}
              options={[
                { value: 'RandomForest', label: 'Random Forest (Fast & Accurate)' },
                { value: 'SVM', label: 'Support Vector Machine (Stable)' },
                { value: 'KNN', label: 'K-Nearest Neighbors (Simple)' }
              ]}
            />
            <SettingToggle 
              label="Auto Re-train"
              value={settings.model.auto_retrain}
              onChange={(v: boolean) => setSettings({...settings, model: {...settings.model, auto_retrain: v}})}
              description="Automatically improve model with new samples"
            />
            <div className="mt-2 pt-2 border-t border-gray-700 flex justify-between text-xs text-gray-400">
              <span>Active Model Version:</span>
              <span className="text-white font-mono">{systemInfo?.model_version || 'v1.0.0'}</span>
            </div>
          </SettingsSection>

        </div>

        {/* RIGHT COLUMN */}
        <div className="space-y-6">
          
          {/* SYSTEM & PERFORMANCE */}
          <SettingsSection icon={<Info className="text-cyan-400" size={20} />} title="System Preferences">
            <SettingToggle 
              label="GPU Acceleration"
              value={settings.system.gpu_acceleration}
              onChange={(v: boolean) => setSettings({...settings, system: {...settings.system, gpu_acceleration: v}})}
              description="Use GPU for faster inference (if available)"
            />
            <SettingToggle 
              label="Auto-Start Cameras"
              value={settings.system.auto_start_cameras}
              onChange={(v: boolean) => setSettings({...settings, system: {...settings.system, auto_start_cameras: v}})}
              description="Reconnect cameras automatically on startup"
            />
            <SettingToggle 
              label="Sound Alerts"
              value={settings.system.sound_alerts}
              onChange={(v: boolean) => setSettings({...settings, system: {...settings.system, sound_alerts: v}})}
              description="Play sound on successful detection"
            />
          </SettingsSection>

          {/* BACKUP & EXPORT (Kluczowe) */}
          <SettingsSection icon={<HardDrive className="text-green-400" size={20} />} title="Backup & Export">
            <div className="grid grid-cols-2 gap-3">
              <button className="py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold flex flex-col items-center justify-center gap-1 transition-colors h-24">
                <Download size={20} className="mb-1 text-blue-400" />
                Export Config
                <span className="text-[10px] text-gray-400 font-normal">Settings JSON</span>
              </button>
              <button className="py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold flex flex-col items-center justify-center gap-1 transition-colors h-24">
                <Upload size={20} className="mb-1 text-green-400" />
                Import Config
                <span className="text-[10px] text-gray-400 font-normal">Restore Settings</span>
              </button>
              <button className="py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold flex flex-col items-center justify-center gap-1 transition-colors h-24">
                <HardDrive size={20} className="mb-1 text-purple-400" />
                Backup Model
                <span className="text-[10px] text-gray-400 font-normal">Save .h5 Model</span>
              </button>
              <button className="py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold flex flex-col items-center justify-center gap-1 transition-colors h-24">
                <HardDrive size={20} className="mb-1 text-orange-400" />
                Export Data
                <span className="text-[10px] text-gray-400 font-normal">Training Samples</span>
              </button>
            </div>
          </SettingsSection>

          {/* SYSTEM STATS */}
          {systemInfo && (
            <div className="bg-black/20 rounded-xl p-4 border border-gray-800 grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-xs text-gray-500 uppercase font-bold">CPU Load</div>
                <div className="text-lg font-bold text-white">{systemInfo.cpu_usage}%</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 uppercase font-bold">RAM Usage</div>
                <div className="text-lg font-bold text-white">{systemInfo.ram_usage}%</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 uppercase font-bold">Disk Free</div>
                <div className="text-lg font-bold text-white">{systemInfo.disk_space}%</div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

// COMPONENTS

const SettingsSection = ({ icon, title, children }: any) => (
  <div className="bg-industrial-gray rounded-xl border border-gray-700 p-5 shadow-lg">
    <h3 className="font-bold text-white flex items-center gap-2 mb-4 pb-3 border-b border-gray-700">
      {icon}
      {title}
    </h3>
    <div className="space-y-4">
      {children}
    </div>
  </div>
);

const SettingSlider = ({ label, value, onChange, min, max, step, unit, multiplier = 1, description }: any) => (
  <div>
    <div className="flex justify-between items-center mb-2">
      <label className="text-sm text-gray-400 font-medium">{label}</label>
      <span className="text-sm font-bold text-white">
        {(value * multiplier).toFixed(multiplier === 100 ? 0 : 0)}{unit}
      </span>
    </div>
    <input 
      type="range"
      min={min}
      max={max}
      step={step}
      value={value}
      onChange={(e) => onChange(parseFloat(e.target.value))}
      className="w-full accent-accent-blue"
    />
    {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
  </div>
);

const SettingToggle = ({ label, value, onChange, description }: any) => (
  <div className="flex items-start justify-between">
    <div className="flex-1">
      <label className="text-sm text-gray-300 font-medium block">{label}</label>
      {description && <p className="text-xs text-gray-500 mt-1">{description}</p>}
    </div>
    <button 
      onClick={() => onChange(!value)}
      className={`relative w-12 h-6 rounded-full transition-colors ${
        value ? 'bg-accent-blue' : 'bg-gray-700'
      }`}
    >
      <div className={`absolute top-1 left-1 w-4 h-4 bg-white rounded-full transition-transform ${
        value ? 'translate-x-6' : ''
      }`} />
    </button>
  </div>
);

const SettingSelect = ({ label, value, onChange, options }: any) => (
  <div>
    <label className="block text-sm text-gray-400 mb-2 font-medium">{label}</label>
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-blue"
    >
      {options.map((opt: any) => (
        <option key={opt.value} value={opt.value}>{opt.label}</option>
      ))}
    </select>
  </div>
);

export default Settings;
