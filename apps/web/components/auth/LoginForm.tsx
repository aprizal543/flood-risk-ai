"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, Check, Loader2 } from "lucide-react";
import { login } from "@/services/auth-api";
import { GoogleButton } from "@/components/auth/GoogleButton";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { useAuth } from "@/hooks/use-auth";
import { useGoogleLogin } from "@/hooks/useGoogleLogin";
import { cn } from "@/lib/utils";

interface LoginErrors {
  email?: string;
  password?: string;
  api?: string;
}

export function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { session, syncSession } = useAuth();
  const { startGoogleLogin, loading: googleLoading, error: googleError } = useGoogleLogin();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState<LoginErrors>({});

  const isEmailValid = useMemo(() => /\S+@\S+\.\S+/.test(email), [email]);
  const oauthError = searchParams.get("oauth_error");
  const apiMessage = errors.api ?? googleError ?? oauthError;

  useEffect(() => {
    if (session) {
      router.replace("/dashboard");
    }
  }, [router, session]);

  if (session) {
    return null;
  }

  const validate = () => {
    const next: LoginErrors = {};
    if (!isEmailValid) next.email = "Masukkan email yang valid.";
    if (password.length < 6) next.password = "Password minimal 6 karakter.";
    setErrors(next);
    return Object.keys(next).length === 0;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (loading || success) return;
    setErrors({});
    if (!validate()) return;

    try {
      setLoading(true);
      const result = await login({ email, password });
      await syncSession(result, { remember: rememberMe });
      setSuccess(true);
      await new Promise((resolve) => setTimeout(resolve, 240));
      router.replace("/dashboard");
      router.refresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Login gagal.";
      setErrors({ api: message });
    } finally {
      if (!success) setLoading(false);
    }
  };

  const busy = loading || success;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      whileHover={{ boxShadow: "0 24px 64px rgba(0,0,0,0.38), 0 0 0 1px rgba(255,255,255,0.035)" }}
      transition={{ duration: 0.3, ease: "easeOut" }}
      className="w-[390px] max-w-[92vw] rounded-[20px] border border-white/[0.105] bg-[#071224]/78 p-8 shadow-[0_22px_58px_rgba(0,0,0,0.34),inset_0_1px_0_rgba(255,255,255,0.045)] backdrop-blur-2xl transition-shadow duration-200"
    >
      <div className="text-center">
        <h2 className="text-[36px] font-bold leading-none tracking-[-0.04em] text-white">Welcome Back</h2>
        <p className="mt-2 text-[15px] font-medium leading-6 text-white/62">Sign in to continue to FloodRisk AI</p>
      </div>

      <form className={cn("mt-7 space-y-[18px]", busy && "cursor-progress")} onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label htmlFor="email" className="text-[13px] font-semibold text-white/78">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={busy}
            className={cn(
              "h-12 w-full rounded-xl border border-white/[0.09] bg-white/[0.035] px-4 text-[15px] text-white outline-none transition-all duration-200 placeholder:text-white/34 placeholder:transition-all hover:border-white/[0.16] focus:border-blue-500/75 focus:bg-white/[0.05] focus:ring-4 focus:ring-blue-500/18 focus:placeholder:pl-1 disabled:cursor-not-allowed disabled:opacity-70",
              errors.email && "border-red-400/70 focus:border-red-400/80 focus:ring-red-500/20"
            )}
            placeholder="you@example.com"
            aria-invalid={Boolean(errors.email)}
            aria-describedby={errors.email ? "login-email-error" : undefined}
          />
          <AnimatePresence>
            {errors.email ? (
              <motion.p id="login-email-error" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.2, ease: "easeOut" }} className="text-xs text-red-300">
                {errors.email}
              </motion.p>
            ) : null}
          </AnimatePresence>
        </div>

        <PasswordInput
          id="password"
          label="Password"
          value={password}
          onChange={setPassword}
          placeholder="Enter your password"
          autoComplete="current-password"
          error={errors.password}
          disabled={busy}
        />

        <div className="flex items-center justify-between gap-4 text-[13px]">
          <label className="group inline-flex cursor-pointer items-center gap-2 text-white/58 transition-colors duration-200 hover:text-white/72">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(event) => setRememberMe(event.target.checked)}
              disabled={busy}
              className="peer sr-only"
            />
            <span className="flex h-4 w-4 items-center justify-center rounded border border-white/18 bg-white/[0.04] text-[10px] text-white transition-all duration-200 group-hover:border-white/30 peer-checked:border-blue-400/80 peer-checked:bg-blue-500 peer-focus-visible:ring-4 peer-focus-visible:ring-blue-500/25 peer-disabled:opacity-60">
              {rememberMe ? <Check className="h-3 w-3" aria-hidden="true" /> : null}
            </span>
            Remember Me
          </label>
          <Link href="#" className="cursor-pointer font-medium text-white/68 underline-offset-4 transition-all duration-150 hover:text-white hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500/30">
            Forgot Password?
          </Link>
        </div>

        <AnimatePresence>
          {apiMessage ? (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }} transition={{ duration: 0.2, ease: "easeOut" }} className="flex items-start gap-2 rounded-xl border border-red-400/35 bg-red-500/10 px-4 py-3 text-sm text-red-200" role="alert" aria-live="polite">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
              <span>{apiMessage}</span>
            </motion.div>
          ) : null}
        </AnimatePresence>

        <motion.button
          type="submit"
          disabled={busy}
          whileHover={!busy ? { scale: 1.01 } : undefined}
          whileTap={!busy ? { scale: 0.99 } : undefined}
          className="inline-flex h-12 w-full items-center justify-center gap-2 rounded-xl bg-[#2563EB] px-4 text-[15px] font-medium text-white shadow-[0_12px_28px_rgba(37,99,235,0.24)] transition-all duration-200 hover:bg-[#3474F4] hover:shadow-[0_14px_32px_rgba(37,99,235,0.3)] focus:outline-none focus:ring-4 focus:ring-blue-500/22 disabled:cursor-progress disabled:opacity-80"
        >
          {success ? <Check className="h-4 w-4" aria-hidden="true" /> : loading ? <Loader2 className="h-4 w-4 animate-spin" aria-hidden="true" /> : null}
          {success ? "Success" : loading ? "Signing In..." : "Sign In"}
        </motion.button>

        <div className="relative py-1">
          <div className="absolute inset-0 flex items-center">
            <span className="w-full border-t border-white/[0.08]" />
          </div>
          <div className="relative flex justify-center text-[11px] font-medium uppercase tracking-[0.22em] text-white/34">
            <span className="bg-[#071224] px-4">OR</span>
          </div>
        </div>

        <GoogleButton label="Continue with Google" disabled={busy || googleLoading} loading={googleLoading} onClick={() => void startGoogleLogin()} />
      </form>

      <p className="mt-[18px] text-center text-[13px] text-white/56">
        Don&apos;t have an account?{" "}
        <Link href="/register" className="font-semibold text-blue-300 underline-offset-4 transition-all duration-150 hover:text-blue-200 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500/30">
          Create Account
        </Link>
      </p>
    </motion.div>
  );
}
