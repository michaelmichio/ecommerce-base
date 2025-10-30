/**
 * 🧭 Role Access Matrix
 * Semua definisi role-based access dikelola di sini.
 *
 * Aturan:
 * - "public"     → Bisa diakses semua orang, tidak perlu login
 * - "protected"  → Hanya bisa diakses jika sudah login (role apa pun)
 * - string[]     → Hanya role tertentu yang boleh
 */
export const routeAccess: Record<string, string[] | "public" | "protected"> = {
  // Public pages
  "/login": "public",
  "/register": "public",
  "/403": "public",

  // Default logged-in pages
  "/": "protected",
  "/products": "protected",

  // Role-specific areas
  "/seller": ["seller", "admin"],
  "/admin": ["admin"],
};

/**
 * 🧩 Fungsi bantu mencari rule berdasarkan path
 * Cocok dengan prefix (misal `/admin/settings` match `/admin`)
 */
export function getAccessRule(pathname: string) {
  const keys = Object.keys(routeAccess);

  // ✅ Urutkan dari path paling panjang → supaya /admin/settings tidak match /a
  const match = keys
    .sort((a, b) => b.length - a.length)
    .find((key) => pathname.startsWith(key));

  // 🔐 Default aman: "protected"
  const rule = match ? routeAccess[match] : "protected";

  // 🛡️ Jika rule adalah array tapi kosong, anggap "protected" (aman)
  if (Array.isArray(rule) && rule.length === 0) return "protected";

  return rule;
}
