export function Divider() {
  return (
    <div className="flex items-center gap-4 py-1 text-xs font-medium uppercase tracking-[0.22em] text-white/35">
      <div className="h-px flex-1 bg-white/[0.08]" />
      <span>OR</span>
      <div className="h-px flex-1 bg-white/[0.08]" />
    </div>
  );
}
