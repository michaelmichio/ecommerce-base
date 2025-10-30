"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useLogin } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import Link from "next/link";
import { toast } from "sonner";
import { useRouter, useSearchParams } from "next/navigation";

const loginSchema = z.object({
  email: z.string().email("Email tidak valid"),
  password: z.string().min(6, "Minimal 6 karakter"),
});

type LoginValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { mutateAsync, isPending } = useLogin();
  const router = useRouter();
  const searchParams = useSearchParams();

  // ✅ ambil parameter redirect dari URL (misal: /login?redirect=/test/123?test=abc)
  const redirectTo = searchParams.get("redirect") || "/products";

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (values: LoginValues) => {
    try {
      await mutateAsync(values);
      toast.success("Berhasil login 🎉");

      // ✅ Redirect ke tujuan awal atau default (/products)
      // hindari open redirect ke domain luar
      if (redirectTo.startsWith("/")) {
        router.push(redirectTo);
      } else {
        router.push("/products");
      }
    } catch (e: any) {
      toast.error(e.message ?? "Login gagal");
    }
  };

  return (
    <div className="max-w-sm mx-auto py-16">
      <h1 className="text-2xl font-bold mb-6">Login</h1>
      <form className="flex flex-col gap-4" onSubmit={handleSubmit(onSubmit)}>
        <Input placeholder="Email" {...register("email")} />
        {errors.email && (
          <p className="text-red-500 text-sm">{errors.email.message}</p>
        )}

        <Input
          type="password"
          placeholder="Password"
          {...register("password")}
        />
        {errors.password && (
          <p className="text-red-500 text-sm">{errors.password.message}</p>
        )}

        <Button type="submit" disabled={isPending}>
          {isPending ? "Memproses..." : "Login"}
        </Button>
      </form>

      <p className="text-sm mt-4">
        Belum punya akun?{" "}
        <Link href="/register" className="underline">
          Daftar
        </Link>
      </p>
    </div>
  );
}
