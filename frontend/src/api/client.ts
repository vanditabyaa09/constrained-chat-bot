import axios from 'axios';

const api = axios.create({
  baseURL: '', // Using proxy
});

export const uploadPDF = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
};

export const chat = async (query: string, history: { role: string; content: string }[]) => {
  const response = await api.post('/chat', { query, history });
  return response.data;
};

export const reset = async () => {
  const response = await api.delete('/reset');
  return response.data;
};
