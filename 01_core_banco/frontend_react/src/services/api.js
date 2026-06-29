import axios from "axios";

export const TOKEN_KEY = "cm_token";
export const USER_KEY = "cm_user";

const ENV_API_URL = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_BASE_URL;

export const API_BASE_URL = (
  ENV_API_URL ||
  (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"
    ? "http://localhost:8003"
    : "https://caja-huancayo-api.onrender.com")
).replace(/\/$/, "");

console.log("API_BASE_URL:", API_BASE_URL);

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);

  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error?.response?.status === 401) {
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
    }

    return Promise.reject(error);
  }
);

export default api;