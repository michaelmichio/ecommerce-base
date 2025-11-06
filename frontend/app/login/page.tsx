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
import { Label } from "@/components/ui/label";
import { useState } from "react";

export function AppIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="141"
      height="32"
      viewBox="0 0 141 32"
      fill="none"
    >
      <g clipPath="url(#clip0_1_3)">
        <path
          fillRule="evenodd"
          clipRule="evenodd"
          d="M12.017 22.4C10.9547 22.4 9.93581 21.9786 9.1846 21.2284C8.43339 20.4783 8.01136 19.4609 8.01136 18.4V0H0V18.4C0 25.0272 5.38043 30.4 12.017 30.4H20.8295V22.4H12.017ZM36.0511 8C35.1043 8 34.1667 8.18623 33.2919 8.54807C32.4171 8.9099 31.6223 9.44025 30.9527 10.1088C30.2832 10.7774 29.7521 11.5711 29.3898 12.4447C29.0274 13.3182 28.8409 14.2545 28.8409 15.2C28.8409 16.1455 29.0274 17.0818 29.3898 17.9553C29.7521 18.8289 30.2832 19.6226 30.9527 20.2912C31.6223 20.9598 32.4171 21.4901 33.2919 21.8519C34.1667 22.2138 35.1043 22.4 36.0511 22.4C37.9634 22.4 39.7974 21.6414 41.1495 20.2912C42.5017 18.9409 43.2614 17.1096 43.2614 15.2C43.2614 13.2904 42.5017 11.4591 41.1495 10.1088C39.7974 8.75857 37.9634 8 36.0511 8ZM20.8295 15.2C20.8295 6.8056 27.6448 0 36.0511 0C44.4575 0 51.2727 6.8056 51.2727 15.2C51.2727 23.5944 44.4575 30.4 36.0511 30.4C27.6448 30.4 20.8295 23.5944 20.8295 15.2ZM122.574 8C120.662 8 118.828 8.75857 117.475 10.1088C116.123 11.4591 115.364 13.2904 115.364 15.2C115.364 17.1096 116.123 18.9409 117.475 20.2912C118.828 21.6414 120.662 22.4 122.574 22.4C124.486 22.4 126.32 21.6414 127.672 20.2912C129.024 18.9409 129.784 17.1096 129.784 15.2C129.784 13.2904 129.024 11.4591 127.672 10.1088C126.32 8.75857 124.486 8 122.574 8ZM107.352 15.2C107.352 6.8056 114.168 0 122.574 0C130.98 0 137.795 6.8056 137.795 15.2C137.795 23.5944 130.98 30.4 122.574 30.4C114.168 30.4 107.352 23.5944 107.352 15.2ZM68.0966 0C59.6903 0 52.875 6.8056 52.875 15.2C52.875 23.5944 59.6903 30.4 68.0966 30.4H90.5284C92.1059 30.4 93.6272 30.16 95.058 29.7152L99.3409 32L103.962 23.3568C105.136 21.1565 105.75 18.7018 105.75 16.2088V15.2C105.75 6.8056 98.9347 0 90.5284 0H68.0966ZM97.7386 15.2C97.7386 13.2904 96.979 11.4591 95.6268 10.1088C94.2746 8.75857 92.4407 8 90.5284 8H68.0966C67.1497 8 66.2121 8.18623 65.3374 8.54807C64.4626 8.9099 63.6677 9.44025 62.9982 10.1088C62.3287 10.7774 61.7976 11.5711 61.4352 12.4447C61.0729 13.3182 60.8864 14.2545 60.8864 15.2C60.8864 16.1455 61.0729 17.0818 61.4352 17.9553C61.7976 18.8289 62.3287 19.6226 62.9982 20.2912C63.6677 20.9598 64.4626 21.4901 65.3374 21.8519C66.2121 22.2138 67.1497 22.4 68.0966 22.4H90.5284C92.431 22.4001 94.2565 21.6492 95.6071 20.311C96.9577 18.9728 97.7238 17.1558 97.7386 15.256V15.2Z"
          fill="#101014"
        />
        <path
          d="M141 2C141 2.53043 140.789 3.03914 140.413 3.41421C140.038 3.78929 139.528 4 138.997 4C138.466 4 137.957 3.78929 137.581 3.41421C137.205 3.03914 136.994 2.53043 136.994 2C136.994 1.46957 137.205 0.960859 137.581 0.585786C137.957 0.210714 138.466 0 138.997 0C139.528 0 140.038 0.210714 140.413 0.585786C140.789 0.960859 141 1.46957 141 2Z"
          fill="#101014"
        />
      </g>
      <defs>
        <clipPath id="clip0_1_3">
          <rect width="141" height="32" fill="white" />
        </clipPath>
      </defs>
    </svg>
  );
}

function EyeIcon() {
  return (
    <svg
      xmlns="http://www.w3.org/2000/svg"
      width="20"
      height="20"
      viewBox="0 0 20 20"
      fill="none"
    >
      <path
        d="M19.3211 9.74688C19.2937 9.68516 18.632 8.21719 17.1609 6.74609C15.2008 4.78594 12.725 3.75 9.99999 3.75C7.27499 3.75 4.79921 4.78594 2.83905 6.74609C1.36796 8.21719 0.703118 9.6875 0.678899 9.74688C0.643362 9.82681 0.625 9.91331 0.625 10.0008C0.625 10.0883 0.643362 10.1748 0.678899 10.2547C0.706243 10.3164 1.36796 11.7836 2.83905 13.2547C4.79921 15.2141 7.27499 16.25 9.99999 16.25C12.725 16.25 15.2008 15.2141 17.1609 13.2547C18.632 11.7836 19.2937 10.3164 19.3211 10.2547C19.3566 10.1748 19.375 10.0883 19.375 10.0008C19.375 9.91331 19.3566 9.82681 19.3211 9.74688ZM9.99999 15C7.5953 15 5.49452 14.1258 3.75546 12.4023C3.0419 11.6927 2.43483 10.8836 1.95312 10C2.4347 9.11636 3.04179 8.30717 3.75546 7.59766C5.49452 5.87422 7.5953 5 9.99999 5C12.4047 5 14.5055 5.87422 16.2445 7.59766C16.9595 8.307 17.5679 9.11619 18.0508 10C17.4875 11.0516 15.0336 15 9.99999 15ZM9.99999 6.25C9.25831 6.25 8.53329 6.46993 7.9166 6.88199C7.29992 7.29404 6.81927 7.87971 6.53544 8.56494C6.25162 9.25016 6.17735 10.0042 6.32205 10.7316C6.46674 11.459 6.82389 12.1272 7.34834 12.6517C7.87279 13.1761 8.54097 13.5333 9.2684 13.6779C9.99583 13.8226 10.7498 13.7484 11.4351 13.4645C12.1203 13.1807 12.7059 12.7001 13.118 12.0834C13.5301 11.4667 13.75 10.7417 13.75 10C13.749 9.00576 13.3535 8.05253 12.6505 7.34949C11.9475 6.64645 10.9942 6.25103 9.99999 6.25ZM9.99999 12.5C9.50554 12.5 9.02219 12.3534 8.61107 12.0787C8.19994 11.804 7.87951 11.4135 7.69029 10.9567C7.50107 10.4999 7.45157 9.99723 7.54803 9.51227C7.64449 9.02732 7.88259 8.58186 8.23222 8.23223C8.58186 7.8826 9.02731 7.6445 9.51227 7.54804C9.99722 7.45157 10.4999 7.50108 10.9567 7.6903C11.4135 7.87952 11.804 8.19995 12.0787 8.61107C12.3534 9.0222 12.5 9.50555 12.5 10C12.5 10.663 12.2366 11.2989 11.7678 11.7678C11.2989 12.2366 10.663 12.5 9.99999 12.5Z"
        fill="#050506"
      />
    </svg>
  );
}

const loginSchema = z.object({
  email: z.string().email("Email tidak valid"),
  password: z.string().min(6, "Minimal 6 karakter"),
});

type LoginValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { mutateAsync, isPending } = useLogin();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [seenPassword, setSeenPassword] = useState<boolean>(false);

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
              <div className="relative">
                <Input
                  {...register("password")}
                  id="password"
                  type={seenPassword ? "text" : "password"}
                  placeholder="Enter password"
                  autoComplete="current-password"
                  className="mt-2 px-3 py-2 pr-11 block w-full font-medium rounded-input text-sm outline-1 -outline-offset-1 outline-neutral-200 placeholder:text-placeholder-500 focus:outline-2 focus:-outline-offset-2 focus:outline-primary-500"
                />
                <div
                  className="cursor-pointer absolute z-10 top-0 right-0 mx-3 my-2"
                  onClick={() => setSeenPassword((prev) => !prev)}
                >
                  <EyeIcon />
                </div>
              </div>
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
                {isPending ? "Processing..." : "Sign in"}
              </Button>
              <p className="text-sm mt-4">
                Not registered yet?{" "}
                <Link href="/register" className="underline">
                  Sign up
                </Link>
              </p>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
