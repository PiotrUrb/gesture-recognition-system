const API_BASE_URL = 'http://localhost:8000';

export interface SystemStatus {
  status: 'online' | 'offline' | 'starting' | 'error' | 'checking';
  cpu_usage?: number;
  memory_usage?: number;
  uptime_seconds?: number;
  backend_responsive?: boolean;
  timestamp?: string;
}

export const systemService = {
  async checkHealth(): Promise<SystemStatus> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (!response.ok) throw new Error('Health check failed');
      const data = await response.json();
      return {
        status: data.status === 'healthy' ? 'online' : 'offline',
        timestamp: new Date().toISOString()
      };
    } catch (error) {
      console.error('Health check error:', error);
      return {
        status: 'offline',
        timestamp: new Date().toISOString()
      };
    }
  },

  connectWebSocket(onMessage: (data: SystemStatus) => void): WebSocket | null {
    try {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      const ws = new WebSocket(`${protocol}//localhost:8000/ws/health`);
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as SystemStatus;
          onMessage(data);
        } catch (e) {
          console.error('WebSocket parse error:', e);
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
      };
      
      return ws;
    } catch (error) {
      console.error('WebSocket connection error:', error);
      return null;
    }
  }
};