"use client";

import Link from "next/link";
import { motion } from "framer-motion";

interface AuthTabsProps {
  active: "login" | "register";
}

export function AuthTabs({ active }: AuthTabsProps) {
  return (
    <nav className="relative mb-10 grid h-12 grid-cols-2 rounded-2xl bg-slate-100 p-1" aria-label="Authentication tabs">
      <Tab href="/login" label="LOGIN" active={active === "login"} />
      <Tab href="/register" label="REGISTER" active={active === "register"} />
    </nav>
  );
}

function Tab({ href, label, active }: { href: string; label: string; active: boolean }) {
  return (
    <Link href={href} className="relative z-10 flex items-center justify-center rounded-xl text-xs font-bold tracking-[0.18em] text-slate-500 transition-colors hover:text-slate-900">
      {active ? <motion.span layoutId="auth-tab" className="absolute inset-0 rounded-xl bg-white shadow-sm" transition={{ duration: 0.28, ease: "easeOut" }} /> : null}
      <span className={`relative ${active ? "text-blue-600" : ""}`}>{label}</span>
      {active ? <span className="absolute bottom-1.5 h-0.5 w-8 rounded-full bg-blue-600" /> : null}
    </Link>
  );
}
