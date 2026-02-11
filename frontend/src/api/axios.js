import axios from "axios";

const api = axios.create({
  baseURL: "/api", // Vite proxy will handle this
  headers: {
    "Content-Type": "application/json",
  },
});

// Token support (future-ready)
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;