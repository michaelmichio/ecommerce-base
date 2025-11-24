import { NextRequest, NextResponse } from "next/server";
import { getAccessRule } from "./app/config/routeAccess";

/* ========================================================================== */
/* Colored logs for development                                               */
/* ========================================================================== */

const COLORS = {
  reset: "\x1b[0m",
  red: "\x1b[91m",
  green: "\x1b[92m",
  yellow: "\x1b[93m",
};

/* ========================================================================== */
/* Safe Redirect Utility                                                      */
/* ========================================================================== */
/**
 * Ensures redirect paths cannot be exploited for open redirect attacks.
 * Safe rules:
 *   - Must start with "/"
 *   - Cannot start with "//"
 *   - Cannot contain "://"
 */
function isSafeRedirectPath(path: string): boolean {
  if (!path) return false;
  if (!path.startsWith("/")) return false;
  if (path.startsWith("//")) return false;
  if (path.includes("://")) return false;
  if (path.length > 2000) return false;
  return true;
}

/* ========================================================================== */
/* JWT Decoder (unsafe but works for role extraction)                          */
/* ========================================================================== */
/**
 * Note: Access token is HttpOnly, but middleware (server) CAN read cookies.
 * So it is safe to decode token *server-side only*.
 */
function decodeJwt<T = any>(token: string): T | null {
  try {
    const payload = token.split(".")[1];
    return JSON.parse(Buffer.from(payload, "base64").toString("utf8"));
  } catch {
    return null;
  }
}

/* ========================================================================== */
/* Logging Helper                                                              */
/* ========================================================================== */
function log(
  path: string,
  action: string,
  reason: string,
  role: string | null
) {
  if (process.env.NODE_ENV !== "development") return;

  const color =
    action === "ALLOW"
      ? COLORS.green
      : action === "REDIRECT"
        ? COLORS.yellow
        : COLORS.red;

  console.log(
    `${color}[${action}]${COLORS.reset} ${path} (${reason}) | role=${
      role ?? "anon"
    }`
  );
}

/* ========================================================================== */
/* Main Proxy Logic                                                            */
/* ========================================================================== */

export function proxy(req: NextRequest) {
  const { pathname, search } = req.nextUrl;

  // Access token from HttpOnly cookie
  const token = req.cookies.get("access_token")?.value ?? null;
  let role: string | null = null;

  const rule = getAccessRule(pathname);

  // PUBLIC ROUTES
  if (rule === "public") {
    if (token && ["/login", "/register"].includes(pathname)) {
      log(pathname, "REDIRECT", "already logged in", role);
      return NextResponse.redirect(new URL("/", req.url));
    }

    log(pathname, "ALLOW", "public route", role);
    return NextResponse.next();
  }

  // PROTECTED ROUTES — require login
  if (!token) {
    log(pathname, "BLOCK", "no token", role);

    const loginUrl = new URL("/login", req.url);
    const hasSearch = !!search;
    const isRoot = pathname === "/";

    if (!isRoot) {
      const redirectPath = hasSearch ? `${pathname}${search}` : pathname;
      if (isSafeRedirectPath(redirectPath)) {
        loginUrl.searchParams.set("redirect", redirectPath);
      }
    }

    return NextResponse.redirect(loginUrl);
  }

  // Decode user role from access token
  const payload = decodeJwt<{ role?: string }>(token);
  role = payload?.role ?? null;

  // Protected for any authenticated user
  if (rule === "protected") {
    log(pathname, "ALLOW", "authenticated user", role);
    return NextResponse.next();
  }

  // Role-based route
  const allowedRoles = Array.isArray(rule) ? rule : [];
  if (!allowedRoles.includes(role || "")) {
    log(pathname, "BLOCK", "forbidden role", role);
    return NextResponse.redirect(new URL("/403", req.url));
  }

  log(pathname, "ALLOW", "role matched", role);
  return NextResponse.next();
}

/* ========================================================================== */
/* Matcher for middleware                                                     */
/* ========================================================================== */
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|upload|api).*)"],
};
