"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import type { Me } from "@/types/auth";

/* ========================================================================== */
/* Login Hook (HttpOnly version)                                              */
/* ========================================================================== */
/**
 * - Calls /auth/login with email/password
 * - Backend sets HttpOnly cookies for tokens
 * - We only invalidate "me" and let middleware + cookies handle the rest
 */
export function useLogin() {
  const qc = useQueryClient();

  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<{ success: boolean; data: any }>(
        "/auth/login",
        payload
      );

      if (!data?.success) {
        throw new Error("Login failed");
      }

      return data.data;
    },
    onSuccess: () => {
      // Refetch current user profile
      qc.invalidateQueries({ queryKey: ["me"] });
    },
  });
}

/* ========================================================================== */
/* Register Hook                                                              */
/* ========================================================================== */
export function useRegister(redirectTo: string = "/login") {
  const qc = useQueryClient();
  const router = useRouter();

  return useMutation({
    mutationFn: async (payload: { email: string; password: string }) => {
      const { data } = await api.post<{ success: boolean; data: any }>(
        "/auth/register",
        payload
      );
      if (!data?.success) {
        throw new Error("Registration failed");
      }
      return data.data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["me"] });
      router.push(redirectTo);
    },
  });
}

/* ========================================================================== */
/* useMe() — Get Logged-in User Profile                                      */
/* ========================================================================== */
/**
 * - Relies entirely on HttpOnly cookie to determine auth state.
 * - If /users/me returns 401 → treat as "not logged in" and return null.
 */
export function useMe() {
  return useQuery({
    queryKey: ["me"],
    queryFn: async () => {
      try {
        const { data } = await api.get<{ success: boolean; data: Me }>(
          "/users/me"
        );
        return data?.data ?? null;
      } catch (err: any) {
        const status = err?.response?.status;
        if (status === 401) {
          // not logged in
          return null;
        }
        console.error("❌ useMe() failed:", err);
        return null;
      }
    },
    staleTime: 60_000,
    retry: false,
  });
}

/* ========================================================================== */
/* logout() — Server-side logout via /auth/logout                            */
/* ========================================================================== */
/**
 * - Calls backend /auth/logout to clear cookies
 * - Then hard-redirects to /login
 */
export async function logout() {
  try {
    await api.post("/auth/logout");
  } catch (e) {
    console.error("Logout failed (ignored):", e);
  }

  if (typeof window !== "undefined") {
    window.location.href = "/login";
  }
}
