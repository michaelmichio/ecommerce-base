"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { setAuthToken, clearAuth, getAuthToken } from "@/lib/authToken";
import type { AuthTokens, Me } from "@/types/auth";

/**
 * 🔐 Login hook
 */
export function useLogin() {
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<{ success: boolean; data: AuthTokens }>(
        "/auth/login",
        payload
      );
      return data.data;
    },
    onSuccess: (tokens) => {
      // ✅ Simpan token di localStorage dan cookie (melalui helper)
      setAuthToken(tokens.access_token);

      // ✅ Simpan cookie manual juga (bisa dibaca oleh middleware)
      const isProd = typeof window !== "undefined" && window.location.protocol === "https:";
      document.cookie = `access_token=${tokens.access_token}; Path=/; SameSite=Lax; ${
        isProd ? "Secure" : ""
      }`;

      // ✅ Refresh data user (me)
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

/**
 * 🧾 Register hook
 */
export function useRegister(redirectTo: string = "/login") {
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<{ success: boolean; data: any }>(
        "/auth/register",
        payload
      );
      if (!data.success) throw new Error("Registration failed");
      return data.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["me"] });
      router.push(redirectTo);
    },
  });
}

/**
 * 👤 Ambil profil user yang sedang login
 */
export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      const token = getAuthToken();
      if (!token) return null; // belum login, hindari 401 spam

      try {
        const { data } = await api.get<{ success: boolean; data: Me }>(
          "/users/me"
        );
        // pastikan ada data
        return data?.data ?? null;
      } catch (err: any) {
        // 🚨 Jika 401 (token invalid / expired), hapus token biar middleware tahu
        if (err.response?.status === 401) {
          clearAuth();
          document.cookie = "access_token=; Max-Age=0; path=/"; // hapus cookie
          return null;
        }

        // Error lain, misalnya network error
        console.error("❌ useMe() failed:", err);
        return null;
      }
    },
    enabled: !!getAuthToken(),
    staleTime: 60_000,
    retry: false,
  });
}

/**
 * 🚪 Logout
 */
export function logout() {
  clearAuth();
  document.cookie = "access_token=; Max-Age=0; path=/"; // ✅ hapus cookie
  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}
