"use client";


import { LogoutButton } from "@/components/LogoutButton";
import { useMe } from "@/hooks/useAuth";

export default function AdminPage() {
  const { data: me } = useMe();

  return (
    <div className="p-6 space-y-4">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-semibold">Admin Dashboard</h1>
        <LogoutButton />
      </div>

      <p className="text-sm text-gray-600">
        Welcome back, <strong>{me?.email}</strong>
      </p>
    </div>
  );
}
