import axios from 'axios';

const API_BASE = '/api/v1';

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
  action_triggered?: string;
  progress?: number;
}

interface Stats {
  total: number;
  successful: number;
  success_rate: number;
  top_gesture: string;
  avg_confidence: number;
}

interface LogsResponse {
  logs: GestureLog[];
  total: number;
  limit: number;
  offset: number;
}

class LogService {
  async getRecentLogs(limit: number = 50): Promise<GestureLog[]> {
    try {
      const response = await axios.get(
        `${API_BASE}/gesture-logs/recent?limit=${limit}`
      );
      return response.data.logs || [];
    } catch (error) {
      console.error('Error fetching recent logs:', error);
      throw error;
    }
  }

  async getAllLogs(
    limit: number = 50,
    offset: number = 0
  ): Promise<LogsResponse> {
    try {
      const response = await axios.get(
        `${API_BASE}/gesture-logs/all?limit=${limit}&offset=${offset}`
      );
      return {
        logs: response.data.logs || [],
        total: response.data.total || 0,
        limit,
        offset
      };
    } catch (error) {
      console.error('Error fetching all logs:', error);
      throw error;
    }
  }

  async getStatistics(): Promise<Stats> {
    try {
      const response = await axios.get(`${API_BASE}/gesture-logs/stats`);
      return response.data.stats || {
        total: 0,
        successful: 0,
        success_rate: 0,
        top_gesture: 'N/A',
        avg_confidence: 0
      };
    } catch (error) {
      console.error('Error fetching statistics:', error);
      throw error;
    }
  }

  async getLogsSince(timestamp: string): Promise<GestureLog[]> {
    try {
      const response = await axios.get(
        `${API_BASE}/gesture-logs/since/${encodeURIComponent(timestamp)}`
      );
      return response.data.logs || [];
    } catch (error) {
      console.error('Error fetching logs since:', error);
      throw error;
    }
  }

  async clearOldLogs(days: number = 7): Promise<{ deleted_count: number }> {
    try {
      const response = await axios.delete(
        `${API_BASE}/gesture-logs/clear-old?days=${days}`
      );
      return {
        deleted_count: response.data.deleted_count || 0
      };
    } catch (error) {
      console.error('Error clearing old logs:', error);
      throw error;
    }
  }

  async clearAllLogs(): Promise<{ deleted_count: number }> {
    try {
      const response = await axios.delete(`${API_BASE}/gesture-logs/clear-all`);
      return {
        deleted_count: response.data.deleted_count || 0
      };
    } catch (error) {
      console.error('Error clearing all logs:', error);
      throw error;
    }
  }
}

export default new LogService();
