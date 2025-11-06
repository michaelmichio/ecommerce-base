"use client";

import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRegister } from "@/hooks/useAuth";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { toast } from "sonner";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Label } from "@/components/ui/label";
import { AppIcon } from "../login/page";

const registerSchema = z.object({
  email: z.string().email("Email tidak valid"),
  password: z.string().min(6, "Minimal 6 karakter").max(72),
});

type RegisterValues = z.infer<typeof registerSchema>;

export default function RegisterPage() {
  const { mutateAsync, isPending } = useRegister();
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (values: RegisterValues) => {
    try {
      await mutateAsync(values);
      toast.success("Registrasi berhasil 🎉, silakan login");
      router.push("/login"); // ⬅️ langsung ke login
    } catch (e: any) {
      toast.error(e.message ?? "Gagal register");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="w-103.5 p-8 border border-neutral-200 rounded-3xl">
        <div>
          <AppIcon />
          <p className="text-sm text-neutral-600 mt-4">
            Enter your username and password correctly
          </p>
        </div>
        <div className="mt-8">
          <form onSubmit={handleSubmit(onSubmit)}>
            <div>
              <Label htmlFor="email" className="text-sm font-medium">
                Username
              </Label>
              <Input
                {...register("email")}
                id="email"
                placeholder="Enter username"
                autoComplete="email"
                className="mt-2 px-3 py-2 block w-full font-medium rounded-input text-sm outline-1 -outline-offset-1 outline-neutral-200 placeholder:text-placeholder-500 focus:outline-2 focus:-outline-offset-2 focus:outline-primary-500"
              />
              {errors.email && (
                <p className="text-red-500 text-sm">{errors.email.message}</p>
              )}
            </div>
            <div className="mt-4">
              <Label htmlFor="password" className="text-sm font-medium">
                Password
              </Label>
              <Input
                {...register("password")}
                id="password"
                type="password"
                placeholder="Enter password"
                autoComplete="current-password"
                className="mt-2 px-3 py-2 block w-full font-medium rounded-input text-sm outline-1 -outline-offset-1 outline-neutral-200 placeholder:text-placeholder-500 focus:outline-2 focus:-outline-offset-2 focus:outline-primary-500"
              />
              {errors.password && (
                <p className="text-red-500 text-sm">
                  {errors.password.message}
                </p>
              )}
            </div>
            <div className="mt-6">
              <Button
                type="submit"
                className="px-4 py-3 text-white flex w-full justify-center rounded-lg bg-primary-500 text-sm font-medium hover:bg-primary-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
                disabled={isPending}
              >
                {isPending ? "Processing..." : "Sign up"}
              </Button>
              <p className="text-sm mt-4">
                Already have an account?{" "}
                <Link href="/login" className="underline">
                  Sign in
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
