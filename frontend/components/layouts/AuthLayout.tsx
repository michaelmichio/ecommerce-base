"use client";

import { useMe, logout } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";

export default function AuthLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { data: me, isLoading } = useMe();

  if (isLoading) {
    return <div className="p-6 text-center text-gray-500">Loading...</div>;
  }

  if (!me) {
    // backup: jika token invalid dan middleware belum redirect
    if (typeof window !== "undefined") window.location.href = "/login";
    return null;
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="border-b p-4 flex justify-between items-center bg-gray-50">
        <div className="font-semibold text-lg">
          👋 Hello, <span className="text-primary">{me.email}</span>
        </div>
        <Button variant="outline" onClick={logout}>
          Logout
        </Button>
      </header>

      {/* Content */}
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
