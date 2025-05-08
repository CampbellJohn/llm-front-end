import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const fetchModels = async () => {
  try {
    const response = await api.get('/models');
    return response.data.models;
  } catch (error) {
    console.error('Error fetching models:', error);
    throw error;
  }
};

export const fetchDefaultConfig = async () => {
  try {
    const response = await api.get('/default-config');
    return response.data;
  } catch (error) {
    console.error('Error fetching default config:', error);
    throw error;
  }
};

export const sendChatRequest = async (messages, model, provider) => {
  try {
    const response = await api.post('/chat', {
      messages,
      model,
      provider,
      stream: false,
    });
    return response.data;
  } catch (error) {
    console.error('Error sending chat request:', error);
    throw error;
  }
};

export default api;