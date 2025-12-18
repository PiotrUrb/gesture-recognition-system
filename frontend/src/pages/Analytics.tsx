/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useCallback } from 'react';
import { 
  BarChart3, 
  Filter, 
  Download, 
  Search,
  TrendingUp,
  Camera,
  Hand,
  Clock,
  Target,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  Loader
} from 'lucide-react';
// import api from '../services/api'; // Zakomentowane, bo używamy demo danych

interface LogEntry {
  id: number;
  timestamp: string;
  gesture: string;
  gesture_label: string;
  camera_id: number;
  camera_name: string;
  confidence: number;
  mode: string;
  hand_type: string;
  message: string;
  success: boolean;
}

interface Stats {
  total_detections: number;
  unique_gestures: number;
  avg_confidence: number;
  cameras_active: number;
  detections_today: number;
  top_gesture: { name: string; count: number };
}

const Analytics = () => {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [filters, setFilters] = useState({
    search: '',
    gesture: '',
    camera: '',
    dateFrom: '',
    dateTo: '',
    minConfidence: 0
  });
  const [showFilters, setShowFilters] = useState(false);

  const logsPerPage = 50;

  // Używamy useCallback, aby funkcje były stabilne w zależnościach useEffect
  const fetchLogs = useCallback(async () => {
    try {
      setIsLoading(true);
      // Symulacja API
      setTimeout(() => {
          setLogs(generateDemoLogs());
          setTotalPages(5);
          setIsLoading(false);
      }, 500);
    } catch (e) {
      console.error('Error fetching logs:', e);
      setLogs(generateDemoLogs());
      setTotalPages(5);
      setIsLoading(false);
    }
  }, []); // Pusta tablica zależności, bo generateDemoLogs jest stabilne

  const fetchStats = useCallback(async () => {
    try {
      setStats({
        total_detections: 12847,
        unique_gestures: 8,
        avg_confidence: 87.3,
        cameras_active: 2,
        detections_today: 342,
        top_gesture: { name: 'Open Hand', count: 4521 }
      });
    } catch (e) {
      console.error('Error fetching stats:', e);
    }
  }, []);

  useEffect(() => {
    fetchLogs();
    fetchStats();
  }, [fetchLogs, fetchStats, currentPage]); // Dodano zależności

  const handleExportCSV = () => {
    const headers = ['Timestamp', 'Gesture', 'Camera', 'Hand', 'Confidence', 'Mode', 'Status'];
    const rows = logs.map(log => [
      new Date(log.timestamp).toLocaleString(),
      log.gesture_label,
      `Camera ${log.camera_id} (${log.camera_name})`,
      log.hand_type,
      `${(log.confidence * 100).toFixed(1)}%`,
      log.mode,
      log.success ? 'Success' : 'Failed'
    ]);

    const csv = [headers, ...rows].map(row => row.join(',')).join('\n');
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gesture-logs-${new Date().toISOString()}.csv`;
    a.click();
  };

  const handleExportJSON = () => {
    const json = JSON.stringify(logs, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gesture-logs-${new Date().toISOString()}.json`;
    a.click();
  };

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col overflow-hidden p-3 lg:p-6 gap-4 lg:gap-6">
      
      {/* STATS HEADER */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 flex-shrink-0">
        <StatsCard 
          icon={<BarChart3 className="text-blue-400" size={20} />}
          label="Total Detections"
          value={stats?.total_detections.toLocaleString() ?? '0'}
        />
        <StatsCard 
          icon={<Hand className="text-yellow-400" size={20} />}
          label="Unique Gestures"
          value={stats?.unique_gestures ?? 0}
        />
        <StatsCard 
          icon={<Target className="text-green-400" size={20} />}
          label="Avg Confidence"
          value={stats ? `${stats.avg_confidence.toFixed(1)}%` : 'N/A'}
        />
        <StatsCard 
          icon={<Camera className="text-purple-400" size={20} />}
          label="Active Cameras"
          value={stats?.cameras_active ?? 0}
        />
        <StatsCard 
          icon={<Clock className="text-orange-400" size={20} />}
          label="Today"
          value={stats?.detections_today ?? 0}
        />
        <StatsCard 
          icon={<TrendingUp className="text-pink-400" size={20} />}
          label="Top Gesture"
          value={stats?.top_gesture.name ?? 'N/A'}
          subtitle={stats ? `${stats.top_gesture.count} times` : undefined}
        />
      </div>

      {/* TOOLBAR */}
      <div className="bg-industrial-gray rounded-xl border border-gray-700 p-3 lg:p-4 flex flex-wrap justify-between items-center shadow-lg gap-3 flex-shrink-0">
        <div className="flex items-center gap-3 flex-1">
          <button 
            onClick={() => setShowFilters(!showFilters)}
            className={`px-3 lg:px-4 py-2 rounded-lg text-sm font-bold flex items-center gap-2 transition-colors ${
              showFilters ? 'bg-accent-blue text-white' : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
            }`}
          >
            <Filter size={16} />
            Filters
          </button>

          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" size={16} />
            <input 
              type="text"
              value={filters.search}
              onChange={(e) => setFilters({...filters, search: e.target.value})}
              placeholder="Search gestures..."
              className="w-full pl-10 pr-4 py-2 bg-gray-800 border border-gray-700 rounded-lg text-white text-sm focus:outline-none focus:border-accent-blue"
            />
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button 
            onClick={handleExportCSV}
            className="px-3 lg:px-4 py-2 bg-green-600 hover:bg-green-500 text-white rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
          >
            <Download size={16} />
            <span className="hidden sm:inline">Export CSV</span>
          </button>
          <button 
            onClick={handleExportJSON}
            className="px-3 lg:px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-sm font-bold flex items-center gap-2 transition-colors"
          >
            <Download size={16} />
            <span className="hidden sm:inline">JSON</span>
          </button>
        </div>
      </div>

      {/* FILTERS PANEL */}
      {showFilters && (
        <div className="bg-industrial-gray rounded-xl border border-gray-700 p-4 shadow-lg flex-shrink-0 animate-in slide-in-from-top-2">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-xs text-gray-400 mb-2 font-bold uppercase">Gesture</label>
              <select
                value={filters.gesture}
                onChange={(e) => setFilters({...filters, gesture: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-blue"
              >
                <option value="">All Gestures</option>
                <option value="fist">Fist</option>
                <option value="open_hand">Open Hand</option>
                <option value="thumbs_up">Thumbs Up</option>
                <option value="peace">Peace</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-2 font-bold uppercase">Camera</label>
              <select
                value={filters.camera}
                onChange={(e) => setFilters({...filters, camera: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-blue"
              >
                <option value="">All Cameras</option>
                <option value="0">Camera 0</option>
                <option value="1">Camera 1</option>
                <option value="2">Camera 2</option>
              </select>
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-2 font-bold uppercase">Date From</label>
              <input 
                type="date"
                value={filters.dateFrom}
                onChange={(e) => setFilters({...filters, dateFrom: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-blue"
              />
            </div>

            <div>
              <label className="block text-xs text-gray-400 mb-2 font-bold uppercase">Date To</label>
              <input 
                type="date"
                value={filters.dateTo}
                onChange={(e) => setFilters({...filters, dateTo: e.target.value})}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-accent-blue"
              />
            </div>
          </div>

          <div className="mt-4 flex justify-end gap-2 border-t border-gray-700 pt-4">
            <button 
              onClick={() => setFilters({search: '', gesture: '', camera: '', dateFrom: '', dateTo: '', minConfidence: 0})}
              className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-white rounded-lg text-sm font-bold transition-colors"
            >
              Reset
            </button>
            <button 
              onClick={fetchLogs}
              className="px-4 py-2 bg-accent-blue hover:bg-blue-500 text-white rounded-lg text-sm font-bold transition-colors"
            >
              Apply Filters
            </button>
          </div>
        </div>
      )}

      {/* LOGS TABLE */}
      <div className="flex-1 bg-industrial-gray rounded-xl border border-gray-700 overflow-hidden flex flex-col shadow-lg min-h-0">
        <div className="overflow-x-auto overflow-y-auto flex-1 custom-scrollbar">
          <table className="w-full text-left text-sm border-collapse min-w-[900px]">
            <thead className="bg-gray-800/90 text-gray-400 border-b border-gray-700 sticky top-0 z-10 backdrop-blur-sm">
              <tr>
                <th className="py-3 px-4 font-bold text-xs uppercase w-40">Timestamp</th>
                <th className="py-3 px-4 font-bold text-xs uppercase w-32">Gesture</th>
                <th className="py-3 px-4 font-bold text-xs uppercase w-40">Camera</th>
                <th className="py-3 px-4 font-bold text-xs uppercase w-24">Hand</th>
                <th className="py-3 px-4 font-bold text-xs uppercase w-32">Confidence</th>
                <th className="py-3 px-4 font-bold text-xs uppercase w-24">Mode</th>
                <th className="py-3 px-4 font-bold text-xs uppercase w-28">Status</th>
                <th className="py-3 px-4 font-bold text-xs uppercase">Message</th>
              </tr>
            </thead>
            <tbody className="text-gray-300 divide-y divide-gray-800/50">
              {isLoading ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    <div className="flex flex-col items-center gap-3">
                      <Loader size={32} className="text-accent-blue animate-spin" />
                      <span>Loading logs...</span>
                    </div>
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={8} className="py-12 text-center text-gray-500">
                    <div className="flex flex-col items-center gap-2">
                        <Hand size={48} className="opacity-20" />
                        <p>No detection logs found</p>
                        <p className="text-xs">Try adjusting your filters</p>
                    </div>
                  </td>
                </tr>
              ) : (
                logs.map((log, idx) => (
                  <tr 
                    key={log.id} 
                    className={`hover:bg-white/5 transition-colors ${idx % 2 === 0 ? 'bg-transparent' : 'bg-gray-800/20'}`}
                  >
                    <td className="py-3 px-4 font-mono text-xs text-gray-400">
                      {new Date(log.timestamp).toLocaleString()}
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">{getGestureEmoji(log.gesture)}</span>
                        <span className="font-bold text-white">{log.gesture_label}</span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <Camera size={14} className="text-purple-400" />
                        <div>
                          <span className="text-white font-medium block">Camera {log.camera_id}</span>
                          <span className="text-[10px] text-gray-500">{log.camera_name}</span>
                        </div>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`px-2 py-1 rounded text-[10px] font-bold uppercase ${
                        log.hand_type === 'Right' ? 'bg-blue-500/20 text-blue-400' : 'bg-green-500/20 text-green-400'
                      }`}>
                        {log.hand_type}
                      </span>
                    </td>
                    <td className="py-3 px-4">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-700 h-1.5 rounded-full overflow-hidden w-16">
                          <div 
                            className={`h-full rounded-full ${
                              log.confidence > 0.8 ? 'bg-green-500' : 
                              log.confidence > 0.5 ? 'bg-yellow-500' : 'bg-red-500'
                            }`}
                            style={{ width: `${log.confidence * 100}%` }}
                          />
                        </div>
                        <span className={`text-xs font-mono font-bold ${
                          log.confidence > 0.8 ? 'text-green-400' : 
                          log.confidence > 0.5 ? 'text-yellow-400' : 'text-red-400'
                        }`}>
                          {(log.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 px-4">
                      <span className="text-xs font-bold text-gray-400 uppercase">{log.mode}</span>
                    </td>
                    <td className="py-3 px-4">
                      <span className={`inline-flex items-center gap-1.5 px-2 py-1 rounded text-[10px] font-bold uppercase border ${
                        log.success ? 'bg-green-500/10 text-green-400 border-green-500/20' : 'bg-red-500/10 text-red-400 border-red-500/20'
                      }`}>
                        {log.success ? <CheckCircle size={12} /> : <XCircle size={12} />}
                        {log.success ? 'Success' : 'Failed'}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-xs text-gray-400 truncate max-w-xs">
                      {log.message}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* PAGINATION */}
        <div className="bg-gray-800/50 border-t border-gray-700 px-4 py-3 flex items-center justify-between flex-shrink-0">
          <div className="text-xs text-gray-400">
            Showing <span className="font-bold text-white">{(currentPage - 1) * logsPerPage + 1}</span> to{' '}
            <span className="font-bold text-white">{Math.min(currentPage * logsPerPage, logs.length)}</span> of{' '}
            <span className="font-bold text-white">{logs.length}</span> entries
          </div>

          <div className="flex items-center gap-2">
            <button 
              onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
              disabled={currentPage === 1}
              className="p-1.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg transition-colors"
            >
              <ChevronLeft size={16} />
            </button>

            <div className="flex gap-1">
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const page = i + 1;
                return (
                  <button
                    key={page}
                    onClick={() => setCurrentPage(page)}
                    className={`px-3 py-1 rounded text-xs font-bold transition-colors ${
                      currentPage === page 
                        ? 'bg-accent-blue text-white' 
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {page}
                  </button>
                );
              })}
            </div>

            <button 
              onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-600 text-white rounded-lg transition-colors"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

// Stats Card Component
const StatsCard = ({ icon, label, value, subtitle }: any) => (
  <div className="bg-industrial-gray rounded-xl border border-gray-700 p-4 flex items-center gap-3 shadow-lg h-full">
    <div className="p-3 bg-black/30 rounded-lg flex-shrink-0">
      {icon}
    </div>
    <div className="flex-1 min-w-0">
      <p className="text-[10px] text-gray-500 uppercase font-bold tracking-wide truncate">{label}</p>
      <p className="text-lg lg:text-xl font-bold text-white truncate">{value}</p>
      {subtitle && <p className="text-[10px] text-gray-400 truncate">{subtitle}</p>}
    </div>
  </div>
);

// Helper Functions
const getGestureEmoji = (gesture: string) => {
  const emojiMap: Record<string, string> = {
    'fist': '✊',
    'open_hand': '✋',
    'thumbs_up': '👍',
    'peace': '✌️',
    'ok_sign': '👌',
    'index_point': '👉',
    'call_me': '🤙',
    'stop': '🖐️'
  };
  return emojiMap[gesture] || '✋';
};

const generateDemoLogs = (): LogEntry[] => {
  const gestures = ['fist', 'open_hand', 'thumbs_up', 'peace'];
  const labels = ['Fist', 'Open Hand', 'Thumbs Up', 'Peace'];
  const cameras = [
    { id: 0, name: 'USB Main' },
    { id: 1, name: 'IP Camera 1' },
    { id: 2, name: 'External' }
  ];
  const modes = ['standard', 'safe', 'all'];
  const hands = ['Left', 'Right'];

  return Array.from({ length: 100 }, (_, i) => {
    const gestureIdx = Math.floor(Math.random() * gestures.length);
    const camera = cameras[Math.floor(Math.random() * cameras.length)];
    const confidence = 0.5 + Math.random() * 0.5;
    const success = confidence > 0.7;

    return {
      id: i + 1,
      timestamp: new Date(Date.now() - i * 60000).toISOString(),
      gesture: gestures[gestureIdx],
      gesture_label: labels[gestureIdx],
      camera_id: camera.id,
      camera_name: camera.name,
      confidence,
      mode: modes[Math.floor(Math.random() * modes.length)],
      hand_type: hands[Math.floor(Math.random() * hands.length)],
      message: success ? 'Action executed successfully' : 'Confidence too low',
      success
    };
  });
};

export default Analytics;
