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
import { useState, useMemo } from "react";
import AppIcon from "@/components/icons/AppIcon";
import EyeIcon from "@/components/icons/EyeIcon";

/* -------------------------------------------------------------------------- */
/*  Login Form Schema (Validation using Zod)                                  */
/* -------------------------------------------------------------------------- */
const loginSchema = z.object({
  email: z.email("Invalid email address."),
  password: z.string().min(6, "At least 6 characters."),
});

type LoginValues = z.infer<typeof loginSchema>;

export default function LoginPage() {
  const { mutateAsync, isPending } = useLogin();
  const router = useRouter();
  const searchParams = useSearchParams();

  const [seenPassword, setSeenPassword] = useState(false);

  /* ---------------------------------------------------------------------- */
  /*  Safe redirect path handling (to prevent open redirect attack)         */
  /* ---------------------------------------------------------------------- */
  const redirectTo = useMemo(() => {
    const redirect = searchParams.get("redirect");

    // If no redirect param → default to dashboard/products
    if (!redirect) return "/products";

    // SECURITY: allow only internal paths
    if (
      redirect.startsWith("/") &&
      !redirect.startsWith("//") &&
      !redirect.includes("://")
    ) {
      return redirect;
    }

    // Fallback if unsafe
    return "/products";
  }, [searchParams]);

  /* ---------------------------------------------------------------------- */
  /*  React Hook Form Setup                                                 */
  /* ---------------------------------------------------------------------- */
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginValues>({
    resolver: zodResolver(loginSchema),
  });

  /* ---------------------------------------------------------------------- */
  /*  Submit Handler                                                        */
  /* ---------------------------------------------------------------------- */
  const onSubmit = async (values: LoginValues) => {
    try {
      await mutateAsync(values);
      toast.success("Welcome back! 🎉");

      router.push(redirectTo);
    } catch (e: any) {
      // Normalize error message
      console.log("xxxe", e);
      const msg =
        e?.response?.data?.message ||
        e?.response?.data?.error?.message ||
        e?.message ||
        "Login failed. Please check your email and password.";

      toast.error(msg);
    }
  };

  /* ---------------------------------------------------------------------- */
  /*  Render                                                                */
  /* ---------------------------------------------------------------------- */
  return (
    <div className="min-h-screen flex items-start md:items-center justify-center">
      <div className="w-103.5 px-4 py-10 md:p-8 md:border md:border-neutral-200 rounded-3xl">
        {/* Header -------------------------------------------------------- */}
        <div>
          <AppIcon />
          <p className="text-sm text-neutral-600 mt-4">
            Enter your username and password correctly
          </p>
        </div>

        {/* Form ---------------------------------------------------------- */}
        <div className="mt-8">
          <form onSubmit={handleSubmit(onSubmit)} noValidate>
            {/* Email ------------------------------------------------------ */}
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

            {/* Password --------------------------------------------------- */}
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

                {/* Password toggle button -------------------------------- */}
                <button
                  type="button"
                  aria-label="Toggle password visibility"
                  className="absolute z-10 top-0 right-0 mx-3 my-2 cursor-pointer"
                  onClick={() => setSeenPassword((prev) => !prev)}
                >
                  <EyeIcon />
                </button>
              </div>

              {errors.password && (
                <p className="text-red-500 text-sm">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Submit Button ---------------------------------------------- */}
            <div className="mt-6">
              <Button
                type="submit"
                className="px-4 py-3 text-white flex w-full justify-center rounded-lg bg-primary-500 text-sm font-medium hover:bg-primary-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-500"
                disabled={isPending}
              >
                {isPending ? "Processing..." : "Sign in"}
              </Button>

              {/* Register Link ------------------------------------------- */}
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
