"use client";

import { motion } from "framer-motion";
import { AnimatedBackground } from "@/components/background/AnimatedBackground";

interface AuthShellProps {
  children: React.ReactNode;
}

export function AuthShell({ children }: AuthShellProps) {
  return (
    <main className="relative flex min-h-screen items-center justify-center overflow-hidden bg-transparent px-4 py-6 text-white sm:px-6 sm:py-8">
      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.2, ease: "easeOut" }}>
        <AnimatedBackground />
      </motion.div>

      <div className="relative z-10 flex w-full justify-center">{children}</div>
    </main>
  );
}
