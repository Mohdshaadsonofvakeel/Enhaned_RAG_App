import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  timeout: 60000,
});

export async function uploadFiles(files) {
  const form = new FormData();
  for (const f of files) form.append('files', f);
  const { data } = await api.post('/api/upload', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function askQuestion(payload) {
  const { data } = await api.post('/api/ask', payload);
  return data;
}

export default api;
