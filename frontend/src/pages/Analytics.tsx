/* eslint-disable @typescript-eslint/no-explicit-any */
import { useEffect, useState } from 'react';
import {
  BarChart3,
  TrendingUp,
  Hand,
  Target,
  ChevronLeft,
  ChevronRight,
  CheckCircle,
  XCircle,
  Loader,
  Trash2,
  RefreshCw
} from 'lucide-react';
import api from '../services/api';

/* ===================== TYPES ===================== */

interface GestureLog {
  id: number;
  timestamp: string;
  gesture: string;
  gesture_label: string;
  confidence: number;
  hand_type: string;
  mode: string;
  success: boolean;
  message: string;
  camera_id: number;
  camera_name: string;
}

interface Stats {
  total: number;
  successful: number;
  success_rate: number;
  top_gesture: string;
  avg_confidence: number;
}

/* ===================== CONFIG ===================== */

const PAGE_SIZE = 50;

/* ===================== COMPONENT ===================== */

const Analytics = () => {
  const [logs, setLogs] = useState<GestureLog[]>([]);
  const [stats, setStats] = useState<Stats | null>(null);
  const [offset, setOffset] = useState(0);
  const [total, setTotal] = useState(0);

  const [loading, setLoading] = useState(true);
  const [isClearing, setIsClearing] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  /* ===================== DATA ===================== */

  const fetchLogs = async (newOffset = offset) => {
    try {
      setLoading(true);
      const res = await api.get(
        `/api/v1/gesture-logs/all?limit=${PAGE_SIZE}&offset=${newOffset}`
      );
      setLogs(res.data.logs || []);
      setTotal(res.data.total || 0);
      setOffset(newOffset);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const res = await api.get('/api/v1/gesture-logs/stats');
      setStats(res.data.stats || null);
    } catch (e) {
      console.error(e);
    }
  };

  /* ===================== WEBSOCKET ===================== */

  useEffect(() => {
    let ws: WebSocket | null = null;

    const connect = () => {
      const proto = location.protocol === 'https:' ? 'wss' : 'ws';
      ws = new WebSocket(`${proto}://localhost:8000/ws/gesture-logs`);

      ws.onmessage = e => {
        const log = JSON.parse(e.data);
        setLogs(prev => [log, ...prev].slice(0, PAGE_SIZE));
        setTotal(t => t + 1);
      };

      ws.onclose = () => setTimeout(connect, 3000);
    };

    fetchLogs(0);
    fetchStats();
    connect();

    return () => ws?.close();
  }, []);

  /* ===================== ACTIONS ===================== */

  const handleClearLogs = async () => {
    try {
      setIsClearing(true);
      await api.delete('/api/v1/gesture-logs/clear-all');
      setLogs([]);
      setTotal(0);
      setOffset(0);
      setShowConfirm(false);
      fetchStats();
    } catch {
      alert('Failed to clear logs');
    } finally {
      setIsClearing(false);
    }
  };

  /* ===================== HELPERS ===================== */

  const totalPages = Math.ceil(total / PAGE_SIZE);
  const currentPage = Math.floor(offset / PAGE_SIZE) + 1;

  const getGestureEmoji = (g: string) =>
    ({
      fist: '✊',
      open_palm: '✋',
      peace: '✌️',
      thumbs_up: '👍',
      ok: '👌'
    }[g] || '🎯');

  /* ===================== RENDER ===================== */

  return (
    <div className="h-[calc(100vh-5rem)] flex flex-col p-6 gap-6">

      {/* ===== STATS ===== */}
      {stats && (
        <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
          <StatsCard icon={<BarChart3 />} label="Total" value={stats.total.toLocaleString()} />
          <StatsCard icon={<Target />} label="Success Rate" value={`${(stats.success_rate * 100).toFixed(1)}%`} />
          <StatsCard icon={<TrendingUp />} label="Top Gesture" value={stats.top_gesture} />
          <StatsCard icon={<Hand />} label="Avg Confidence" value={`${(stats.avg_confidence * 100).toFixed(0)}%`} />
          <button
            onClick={() => setShowConfirm(true)}
            className="bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 rounded-xl flex flex-col items-center justify-center"
          >
            <Trash2 className="text-red-400" />
            <span className="text-xs text-red-400">Clear all</span>
          </button>
        </div>
      )}

      {/* ===== TABLE ===== */}
      <div className="flex-1 bg-industrial-gray border border-gray-700 rounded-xl overflow-hidden flex flex-col">
        <div className="overflow-auto flex-1">
          <table className="w-full text-sm">
            <thead className="sticky top-0 bg-gray-800 text-gray-400">
              <tr>
                <th className="p-3">Time</th>
                <th>Gesture</th>
                <th>Camera</th>
                <th>Confidence</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr>
                  <td colSpan={5} className="py-12 text-center">
                    <Loader className="animate-spin mx-auto" />
                  </td>
                </tr>
              ) : (
                logs.map(log => (
                  <tr key={log.id} className="hover:bg-white/5">
                    <td className="p-3 font-mono text-xs">
                      {new Date(log.timestamp).toLocaleTimeString()}
                    </td>
                    <td className="flex items-center gap-2 p-3">
                      {getGestureEmoji(log.gesture)}
                      <span className="font-bold">{log.gesture_label}</span>
                    </td>
                    <td className="p-3">{log.camera_name}</td>
                    <td className="p-3">{(log.confidence * 100).toFixed(0)}%</td>
                    <td className="p-3">
                      {log.success ? (
                        <CheckCircle className="text-green-400" size={16} />
                      ) : (
                        <XCircle className="text-red-400" size={16} />
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* ===== PAGINATION ===== */}
        <div className="border-t border-gray-700 p-3 flex justify-between">
          <span className="text-xs text-gray-400">
            Page {currentPage} / {totalPages}
          </span>
          <div className="flex gap-2">
            <button
              onClick={() => fetchLogs(offset - PAGE_SIZE)}
              disabled={currentPage === 1}
            >
              <ChevronLeft />
            </button>
            <button
              onClick={() => fetchLogs(offset + PAGE_SIZE)}
              disabled={currentPage === totalPages}
            >
              <ChevronRight />
            </button>
          </div>
        </div>
      </div>

      {/* ===== CONFIRM MODAL ===== */}
      {showConfirm && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center">
          <div className="bg-gray-800 p-6 rounded-xl border border-red-500/30">
            <h2 className="text-lg font-bold mb-4">Delete all logs?</h2>
            <div className="flex gap-3">
              <button onClick={() => setShowConfirm(false)}>Cancel</button>
              <button
                onClick={handleClearLogs}
                className="bg-red-600 px-4 py-2 rounded"
              >
                {isClearing ? <RefreshCw className="animate-spin" /> : 'Delete'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/* ===================== STATS CARD ===================== */

const StatsCard = ({ icon, label, value }: any) => (
  <div className="bg-industrial-gray border border-gray-700 rounded-xl p-4 flex gap-3 items-center">
    <div className="p-2 bg-black/30 rounded">{icon}</div>
    <div>
      <p className="text-xs text-gray-400 uppercase">{label}</p>
      <p className="text-xl font-bold">{value}</p>
    </div>
  </div>
);

export default Analytics;
