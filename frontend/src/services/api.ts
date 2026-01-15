import axios from 'axios';

const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const systemService = {
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
  
  getInfo: async () => {
    const response = await api.get('/info');
    return response.data;
  }
};

export default api;
