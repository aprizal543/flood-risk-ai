export function AnimatedBackground() {
  return (
    <div
      className="pointer-events-none fixed inset-0 h-screen w-screen overflow-hidden"
      aria-hidden="true"
      style={{
        background:
          "radial-gradient(circle at 50% 42%, rgba(59, 130, 246, 0.08) 0%, rgba(10, 25, 48, 0.06) 34%, rgba(2, 8, 23, 0) 66%), linear-gradient(180deg, #020817 0%, #071224 48%, #0A1930 100%)",
      }}
    >
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(255,255,255,0.018)_0%,rgba(2,8,23,0)_42%,rgba(2,8,23,0.46)_100%)]" />
    </div>
  );
}
