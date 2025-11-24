import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";

/* ========================================================================== */
/* Axios Instance (withCredentials = true to send HttpOnly cookies)           */
/* ========================================================================== */

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  withCredentials: true, // REQUIRED for HttpOnly cookie auth
});

/* ========================================================================== */
/* Request Interceptor                                                         */
/* ========================================================================== */
/**
 * For HttpOnly cookie authentication, NO Authorization header is needed.
 * Cookies are automatically attached by the browser.
 *
 * So this interceptor simply returns the config unchanged.
 */
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  return config;
});

/* ========================================================================== */
/* Token Refresh Handling (401 → refresh flow)                                 */
/* ========================================================================== */

type RefreshableConfig = InternalAxiosRequestConfig & { _retry?: boolean };

let isRefreshing = false;
let refreshSubscribers: Array<() => void> = [];

/** Queue a request to wait for new token */
function subscribeTokenRefresh(cb: () => void) {
  refreshSubscribers.push(cb);
}

/** Resolve all queued requests */
function onRefreshed() {
  refreshSubscribers.forEach((cb) => cb());
  refreshSubscribers = [];
}

/** Hard logout */
function forceLogout() {
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}

/* ========================================================================== */
/* Response Interceptor                                                        */
/* ========================================================================== */

api.interceptors.response.use(
  (response) => response,

  async (error: AxiosError) => {
    const originalRequest = error.config as RefreshableConfig | undefined;

    if (!originalRequest) return Promise.reject(error);

    const status = error.response?.status;

    // Only handle 401
    if (status !== 401) {
      return Promise.reject(error);
    }

    const url = originalRequest.url || "";

    // Never refresh for these endpoints
    if (
      url.includes("/auth/login") ||
      url.includes("/auth/register") ||
      url.includes("/auth/logout") ||
      url.includes("/auth/refresh")
    ) {
      return Promise.reject(error);
    }

    // Prevent infinite retry loop
    if (originalRequest._retry) {
      forceLogout();
      return Promise.reject(error);
    }

    originalRequest._retry = true;

    /* ---------------- Wait if another refresh is in progress -------------- */
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        subscribeTokenRefresh(() => {
          api(originalRequest).then(resolve).catch(reject);
        });
      });
    }

    /* ---------------- Start refresh flow ---------------------------------- */
    isRefreshing = true;

    try {
      await axios.post(
        `${process.env.NEXT_PUBLIC_API_URL}/auth/refresh`,
        {},
        { withCredentials: true }
      );

      // Now cookies have the new access token
      onRefreshed();

      return api(originalRequest);
    } catch (refreshErr) {
      console.error("[API] Refresh failed:", refreshErr);
      forceLogout();
      return Promise.reject(refreshErr);
    } finally {
      isRefreshing = false;
    }
  }
);

export default api;
