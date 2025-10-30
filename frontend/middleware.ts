import { NextRequest, NextResponse } from "next/server";
import { getAccessRule } from "./app/config/routeAccess";

/** 🎨 Warna ANSI untuk log (hanya tampil di dev) */
const COLORS = {
  reset: "\x1b[0m",
  gray: "\x1b[90m",
  red: "\x1b[91m",
  green: "\x1b[92m",
  yellow: "\x1b[93m",
  blue: "\x1b[94m",
  cyan: "\x1b[96m",
};

/** 🔐 Decode JWT aman (tanpa lib eksternal) */
function decodeJwt<T = any>(token: string): T | null {
  try {
    const json = Buffer.from(token.split(".")[1], "base64").toString("utf-8");
    return JSON.parse(json);
  } catch {
    return null;
  }
}

/** 🧠 Middleware utama */
export function middleware(req: NextRequest) {
  const { pathname, search } = req.nextUrl;
  const token = req.cookies.get("access_token")?.value ?? null;
  const rule = getAccessRule(pathname);

  let role: string | null = null;

  console.log("🧩 Middleware hit:", pathname);

  // 1️⃣ Public route
  if (rule === "public") {
    if (token && ["/login", "/register"].includes(pathname)) {
      logRequest(pathname, "REDIRECT", "already logged in", role);
      return NextResponse.redirect(new URL("/", req.url));
    }
    logRequest(pathname, "ALLOW", "public route", role);
    return NextResponse.next();
  }

  // 2️⃣ Protected route → butuh login
  if (!token) {
    logRequest(pathname, "BLOCK", "no token", role);

    // ✅ Tambahkan redirect param (ingatkan user kembali ke tujuan awal)
    const loginUrl = new URL("/login", req.url);
    const redirectPath = pathname + search;
    if (redirectPath.startsWith("/")) {
      loginUrl.searchParams.set("redirect", redirectPath);
    }

    return NextResponse.redirect(loginUrl);
  }

  // 3️⃣ Decode token dan ambil role
  const payload = decodeJwt<{ role?: string }>(token);
  role = payload?.role ?? null;

  // 4️⃣ Jika rule = protected → semua login boleh
  if (rule === "protected") {
    logRequest(pathname, "ALLOW", "protected route (any role)", role);
    return NextResponse.next();
  }

  // 5️⃣ Jika role tidak termasuk
  const allowedRoles = Array.isArray(rule) ? rule : [];
  if (!allowedRoles.includes(role ?? "")) {
    logRequest(pathname, "BLOCK", `role=${role ?? "null"} not allowed`, role);
    return NextResponse.redirect(new URL("/403", req.url));
  }

  // ✅ Lolos semua
  logRequest(pathname, "ALLOW", `role=${role}`, role);
  return NextResponse.next();
}

/** 🧾 Logger warna untuk dev */
function logRequest(
  path: string,
  action: string,
  reason: string,
  role: string | null
) {
  if (process.env.NODE_ENV === "development") {
    const color =
      action === "ALLOW"
        ? "\x1b[92m"
        : action === "REDIRECT"
        ? "\x1b[93m"
        : "\x1b[91m";
    console.log(
      `${color}[${action}]${COLORS.reset} ${path} (${reason}) | role=${
        role ?? "anon"
      }`
    );
  }
}

/** 🌐 Matcher: aktif di semua halaman kecuali aset statis */
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|upload|api).*)"],
};
