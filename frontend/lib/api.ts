import axios from "axios";
import { clearAuth, getAuthToken, setAuthToken } from "./authToken";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true, // penting untuk kirim cookie refresh_token
});

// 🟢 Inject bearer token ke setiap request
api.interceptors.request.use((config) => {
  const token = getAuthToken();
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ===========================================================
// 🔁 Auto Refresh Token jika dapat 401 dari server
// ===========================================================
let isRefreshing = false;
let refreshSubscribers: ((token: string) => void)[] = [];

function subscribeTokenRefresh(cb: (token: string) => void) {
  refreshSubscribers.push(cb);
}

function onRefreshed(token: string) {
  refreshSubscribers.forEach((cb) => cb(token));
  refreshSubscribers = [];
}

api.interceptors.response.use(
  (res) => res,
  async (error) => {
    const originalRequest = error.config;

    // jika unauthorized dan belum dicoba refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      if (isRefreshing) {
        // 🚦 tunggu refresh token selesai
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            resolve(api(originalRequest));
          });
        });
      }

      isRefreshing = true;
      try {
        console.log("[API] 401 → refreshing token...");

        // 🧠 minta token baru ke backend
        const { data } = await axios.post(
          `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`,
          {},
          { withCredentials: true }
        );

        const newToken = data?.data?.access_token;
        if (newToken) {
          setAuthToken(newToken);
          api.defaults.headers.Authorization = `Bearer ${newToken}`;
          onRefreshed(newToken); // update semua request yang tertunda

          console.log("[API] 🔄 Token refreshed successfully");

          return api(originalRequest);
        }
      } catch (err) {
        // ❌ refresh gagal → logout user
        clearAuth();
        if (typeof window !== "undefined") window.location.href = "/login";
        return Promise.reject(err);
      } finally {
        isRefreshing = false;
      }
    }

    // kalau bukan 401 → lempar error biasa
    return Promise.reject(error);
  }
);

export default api;
