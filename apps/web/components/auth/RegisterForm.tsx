"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import { AlertCircle, Check, Loader2 } from "lucide-react";
import { register } from "@/services/auth-api";
import { GoogleButton } from "@/components/auth/GoogleButton";
import { PasswordInput } from "@/components/auth/PasswordInput";
import { useAuth } from "@/hooks/use-auth";
import { useGoogleLogin } from "@/hooks/useGoogleLogin";
import { cn } from "@/lib/utils";

interface RegisterErrors {
  fullName?: string;
  email?: string;
  password?: string;
  confirmPassword?: string;
  terms?: string;
  api?: string;
}

export function RegisterForm() {
  const router = useRouter();
  const { session } = useAuth();
  const { startGoogleLogin, loading: googleLoading, error: googleError } = useGoogleLogin();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [agreeTerms, setAgreeTerms] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [errors, setErrors] = useState<RegisterErrors>({});

  const isEmailValid = useMemo(() => /\S+@\S+\.\S+/.test(email), [email]);

  useEffect(() => {
    if (session) {
      router.replace("/dashboard");
    }
  }, [router, session]);

  if (session) {
    return null;
  }

  const apiMessage = errors.api ?? googleError;

  const validate = () => {
    const next: RegisterErrors = {};
    if (fullName.trim().length < 2) next.fullName = "Full name minimal 2 karakter.";
    if (!isEmailValid) next.email = "Masukkan email yang valid.";
    if (password.length < 6) next.password = "Password minimal 6 karakter.";
    if (confirmPassword !== password) next.confirmPassword = "Password tidak sama.";
    if (!agreeTerms) next.terms = "Anda harus menyetujui Terms.";
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
      await register({ email, password, full_name: fullName });
      setSuccess(true);
      await new Promise((resolve) => setTimeout(resolve, 240));
      router.replace("/login?registered=1");
      router.refresh();
    } catch (error) {
      const message = error instanceof Error ? error.message : "Registrasi gagal.";
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
      className="w-[400px] max-w-[92vw] rounded-[20px] border border-white/[0.105] bg-[#071224]/78 p-8 shadow-[0_22px_58px_rgba(0,0,0,0.34),inset_0_1px_0_rgba(255,255,255,0.045)] backdrop-blur-2xl transition-shadow duration-200"
    >
      <div className="text-center">
        <h2 className="text-[36px] font-bold leading-none tracking-[-0.04em] text-white">Create Account</h2>
        <p className="mt-2 text-[15px] font-medium leading-6 text-white/62">Start using FloodRisk AI today</p>
      </div>

      <form className={cn("mt-7 space-y-[14px]", busy && "cursor-progress")} onSubmit={handleSubmit}>
        <div className="space-y-2">
          <label htmlFor="fullName" className="text-[13px] font-semibold text-white/78">Full Name</label>
          <input
            id="fullName"
            name="fullName"
            type="text"
            autoComplete="name"
            autoFocus
            value={fullName}
            onChange={(event) => setFullName(event.target.value)}
            disabled={busy}
            className={cn(
              "h-12 w-full rounded-xl border border-white/[0.09] bg-white/[0.035] px-4 text-[15px] text-white outline-none transition-all duration-200 placeholder:text-white/34 placeholder:transition-all hover:border-white/[0.16] focus:border-blue-500/75 focus:bg-white/[0.05] focus:ring-4 focus:ring-blue-500/18 focus:placeholder:pl-1 disabled:cursor-not-allowed disabled:opacity-70",
              errors.fullName && "border-red-400/70 focus:border-red-400/80 focus:ring-red-500/20"
            )}
            placeholder="Your name"
            aria-invalid={Boolean(errors.fullName)}
            aria-describedby={errors.fullName ? "register-fullname-error" : undefined}
          />
          <AnimatePresence>
            {errors.fullName ? (
              <motion.p id="register-fullname-error" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.2, ease: "easeOut" }} className="text-xs text-red-300">
                {errors.fullName}
              </motion.p>
            ) : null}
          </AnimatePresence>
        </div>

        <div className="space-y-2">
          <label htmlFor="email" className="text-[13px] font-semibold text-white/78">Email</label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            disabled={busy}
            className={cn(
              "h-12 w-full rounded-xl border border-white/[0.09] bg-white/[0.035] px-4 text-[15px] text-white outline-none transition-all duration-200 placeholder:text-white/34 placeholder:transition-all hover:border-white/[0.16] focus:border-blue-500/75 focus:bg-white/[0.05] focus:ring-4 focus:ring-blue-500/18 focus:placeholder:pl-1 disabled:cursor-not-allowed disabled:opacity-70",
              errors.email && "border-red-400/70 focus:border-red-400/80 focus:ring-red-500/20"
            )}
            placeholder="you@example.com"
            aria-invalid={Boolean(errors.email)}
            aria-describedby={errors.email ? "register-email-error" : undefined}
          />
          <AnimatePresence>
            {errors.email ? (
              <motion.p id="register-email-error" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.2, ease: "easeOut" }} className="text-xs text-red-300">
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
          placeholder="Minimum 6 characters"
          autoComplete="new-password"
          error={errors.password}
          disabled={busy}
        />

        <PasswordInput
          id="confirmPassword"
          label="Confirm Password"
          value={confirmPassword}
          onChange={setConfirmPassword}
          placeholder="Repeat your password"
          autoComplete="new-password"
          error={errors.confirmPassword}
          disabled={busy}
        />

        <label className={cn("group flex cursor-pointer items-start gap-3 rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-3 text-[13px] text-white/62 transition-all duration-200 hover:border-white/[0.14] hover:bg-white/[0.045]", errors.terms && "border-red-400/50 bg-red-500/10")}>
          <input
            type="checkbox"
            checked={agreeTerms}
            onChange={(event) => setAgreeTerms(event.target.checked)}
            disabled={busy}
            aria-invalid={Boolean(errors.terms)}
            aria-describedby={errors.terms ? "register-terms-error" : undefined}
            className="peer sr-only"
          />
          <span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded border border-white/18 bg-white/[0.04] text-[10px] text-white transition-all duration-200 group-hover:border-white/30 peer-checked:border-blue-400/80 peer-checked:bg-blue-500 peer-focus-visible:ring-4 peer-focus-visible:ring-blue-500/25 peer-disabled:opacity-60">
            {agreeTerms ? <Check className="h-3 w-3" aria-hidden="true" /> : null}
          </span>
          <span>
            I agree to the <span className="font-semibold text-white/82">Terms &amp; Conditions</span>
          </span>
        </label>
        <AnimatePresence>
          {errors.terms ? (
            <motion.p id="register-terms-error" initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -4 }} transition={{ duration: 0.2, ease: "easeOut" }} className="text-xs text-red-300">
              {errors.terms}
            </motion.p>
          ) : null}
        </AnimatePresence>

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
          {success ? "Success" : loading ? "Creating..." : "Create Account"}
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
        Already have an account?{" "}
        <Link href="/login" className="font-semibold text-blue-300 underline-offset-4 transition-all duration-150 hover:text-blue-200 hover:underline focus:outline-none focus:ring-2 focus:ring-blue-500/30">
          Login
        </Link>
      </p>
    </motion.div>
  );
}
