"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";
import { cn } from "@/lib/utils";

interface PasswordInputProps {
  id: string;
  label: string;
  value?: string;
  onChange?: (value: string) => void;
  placeholder?: string;
  error?: string;
  autoComplete?: string;
  disabled?: boolean;
}

export function PasswordInput({ id, label, value, onChange, placeholder, error, autoComplete, disabled = false }: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="text-[13px] font-semibold text-white/78">
        {label}
      </label>
      <div
        className={cn(
          "group flex h-12 items-center gap-3 rounded-xl border border-white/[0.09] bg-white/[0.035] px-4 transition-all duration-200 hover:border-white/[0.16]",
          "focus-within:border-blue-500/75 focus-within:bg-white/[0.05] focus-within:ring-4 focus-within:ring-blue-500/18",
          error && "border-red-400/70 focus-within:border-red-400/80 focus-within:ring-red-500/20",
          disabled && "opacity-70"
        )}
      >
        <input
          id={id}
          name={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={(event) => onChange?.(event.target.value)}
          placeholder={placeholder}
          autoComplete={autoComplete}
          disabled={disabled}
          className="w-full border-0 bg-transparent text-[15px] text-white outline-none transition-all duration-200 placeholder:text-white/34 placeholder:transition-all focus:placeholder:pl-1 disabled:cursor-not-allowed"
          aria-invalid={Boolean(error)}
          aria-describedby={error ? `${id}-error` : undefined}
        />
        <motion.button
          type="button"
          onClick={() => setVisible((current) => !current)}
          disabled={disabled}
          animate={{ rotate: visible ? 8 : 0 }}
          transition={{ duration: 0.18, ease: "easeOut" }}
          className="inline-flex h-8 w-8 shrink-0 items-center justify-center rounded-lg text-white/42 transition-colors duration-200 hover:bg-white/[0.06] hover:text-white focus:outline-none focus:ring-2 focus:ring-blue-500/30 disabled:cursor-not-allowed"
          aria-label={visible ? "Hide password" : "Show password"}
        >
          {visible ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
        </motion.button>
      </div>
      {error && (
        <motion.p id={`${id}-error`} initial={{ opacity: 0, y: -4 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.2, ease: "easeOut" }} className="text-xs text-red-300">
          {error}
        </motion.p>
      )}
    </div>
  );
}
