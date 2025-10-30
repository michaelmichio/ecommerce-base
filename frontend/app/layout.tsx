"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "@/lib/queryClient";
import { Toaster } from "sonner"; // ✅ untuk notifikasi
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <QueryClientProvider client={queryClient}>
          {children}

          {/* ✅ Komponen toast global */}
          <Toaster richColors position="top-center" />
        </QueryClientProvider>
      </body>
    </html>
  );
}
