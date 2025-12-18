import axios from 'axios';

// Adres Twojego backendu (FastAPI)
const API_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Funkcje do pobierania danych
export const systemService = {
  // Sprawdza czy backend żyje
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },
  
  // Pobiera informacje o systemie
  getInfo: async () => {
    const response = await api.get('/info');
    return response.data;
  }
};

export default api;
