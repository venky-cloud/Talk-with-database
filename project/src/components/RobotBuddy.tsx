export default function RobotBuddy() {
  return (
    <div className="fixed bottom-6 right-6 z-[10000] select-none pointer-events-none">
      <div className="robot-bob">
        <svg className="robot-giggle" width="92" height="92" viewBox="0 0 128 128" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="g1" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#34d399"/>
              <stop offset="100%" stopColor="#06b6d4"/>
            </linearGradient>
          </defs>
          <g filter="url(#f1)">
            <rect x="16" y="18" rx="16" ry="16" width="96" height="64" fill="#0f172a" stroke="url(#g1)" strokeWidth="3"/>
            <circle cx="48" cy="50" r="6" fill="#22d3ee"/>
            <circle cx="80" cy="50" r="6" fill="#22d3ee"/>
            <rect x="38" y="62" width="52" height="6" rx="3" fill="#10b981" opacity="0.6"/>
            <rect x="36" y="88" rx="20" ry="20" width="56" height="28" fill="#e5e7eb" opacity="0.9"/>
            <rect x="28" y="84" rx="4" ry="4" width="12" height="22" fill="#e5e7eb" opacity="0.8"/>
            <rect x="88" y="84" rx="4" ry="4" width="12" height="22" fill="#e5e7eb" opacity="0.8"/>
          </g>
          <defs>
            <filter id="f1" x="0" y="0" width="128" height="128" colorInterpolationFilters="sRGB">
              <feDropShadow dx="0" dy="4" stdDeviation="4" floodColor="#10b981" floodOpacity="0.35"/>
            </filter>
          </defs>
        </svg>
      </div>
    </div>
  );
}
