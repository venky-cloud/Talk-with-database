export default function DeerLoader({ label = 'Loading...' }: { label?: string }) {
  return (
    <div className="w-full h-full flex items-center justify-center">
      <div className="relative w-[320px] h-[140px]">
        <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-emerald-900/10 to-transparent border border-emerald-500/20" />
        <div className="absolute left-0 right-0 bottom-6 h-1 bg-gradient-to-r from-transparent via-emerald-500/30 to-transparent blur-[2px]" />
        <div className="deer-run absolute left-0 bottom-8 text-4xl select-none">
          <span className="block">🦌</span>
        </div>
        <div className="absolute right-0 top-0 text-emerald-400/70 text-sm animate-pulse">
          {label}
        </div>
      </div>
    </div>
  );
}
