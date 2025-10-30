"use client";

import { logout } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { LogOut } from "lucide-react"; // jika pakai lucide-react icons

export function LogoutButton({ className }: { className?: string }) {
  return (
    <Button
      onClick={logout}
      variant="outline"
      className={`flex items-center gap-2 ${className ?? ""}`}
    >
      <LogOut size={16} />
      <span>Logout</span>
    </Button>
  );
}
