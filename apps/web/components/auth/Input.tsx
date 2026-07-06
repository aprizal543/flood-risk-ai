import { cn } from "@/lib/utils";

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label: string;
}

export function Input({ label, id, className, ...props }: InputProps) {
  const inputId = id ?? props.name;

  return (
    <div className="space-y-2">
      <label htmlFor={inputId} className="text-sm font-medium text-white/80">
        {label}
      </label>
      <input
        id={inputId}
        className={cn(
          "h-[52px] w-full rounded-[14px] border border-white/[0.08] bg-white/[0.04] px-4 text-[15px] text-white outline-none transition-all duration-200 placeholder:text-white/35",
          "focus:border-blue-500/70 focus:bg-white/[0.06] focus:ring-4 focus:ring-blue-500/20",
          className
        )}
        {...props}
      />
    </div>
  );
}
