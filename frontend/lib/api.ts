import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000",
  withCredentials: false,
});

// (optional) handle error format backend kamu
api.interceptors.response.use(
  (res) => res,
  (error) => {
    const msg =
      error.response?.data?.error?.message || error.message || "Unknown error";
    console.error("API Error:", msg);
    return Promise.reject(new Error(msg));
  }
);

export default api;
