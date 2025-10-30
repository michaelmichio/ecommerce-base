let memoryToken: string | null = null;
const KEY = "access_token"; // ✅ gunakan nama cookie yang sama dengan middleware & backend

/**
 * Simpan token ke memori, localStorage, dan cookie
 */
export function setAuthToken(token: string) {
  memoryToken = token;
  console.log("🔐 Saving token:", token);

  try {
    if (typeof window === "undefined") return;

    // 🧠 Simpan di localStorage
    localStorage.setItem(KEY, token);

    // 🌐 Simpan juga di cookie agar bisa dibaca middleware Next.js
    const isProd = window.location.protocol === "https:";
    document.cookie = `${KEY}=${token}; Path=/; Max-Age=86400; SameSite=Lax; ${
      isProd ? "Secure" : ""
    }`;
  } catch (err) {
    console.warn("⚠️ Failed to save auth token:", err);
  }
}

/**
 * Ambil token dari memori → localStorage → cookie (fallback)
 */
export function getAuthToken(): string | null {
  if (memoryToken) return memoryToken;

  if (typeof window === "undefined") return null;

  try {
    // 🔍 Cek dari localStorage dulu
    const stored = localStorage.getItem(KEY);
    if (stored) {
      memoryToken = stored;
      return stored;
    }

    // 🔍 Fallback ke cookie
    const cookie = document.cookie
      .split("; ")
      .find((row) => row.startsWith(`${KEY}=`));
    if (cookie) {
      const value = cookie.split("=")[1];
      memoryToken = value;
      return value;
    }
  } catch (err) {
    console.warn("⚠️ Failed to get auth token:", err);
  }

  return null;
}

/**
 * Hapus semua token dari memori, localStorage, dan cookie (logout)
 */
export function clearAuth() {
  memoryToken = null;

  if (typeof window === "undefined") return;

  try {
    // ❌ Hapus dari localStorage
    localStorage.removeItem(KEY);

    // ❌ Hapus cookie
    document.cookie = `${KEY}=; Path=/; Max-Age=0;`;
  } catch (err) {
    console.warn("⚠️ Failed to clear auth token:", err);
  }
}
