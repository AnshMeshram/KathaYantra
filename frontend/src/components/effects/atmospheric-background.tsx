"use client";

export function AtmosphericBackground() {
  return (
    <div
      className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      aria-hidden="true"
    >
      {/* Archival Vignette */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_50%_0%,rgba(33,36,49,0.35)_0%,transparent_75%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_80%_80%,rgba(19,20,27,0.5)_0%,transparent_70%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_20%_90%,rgba(12,13,18,0.7)_0%,transparent_60%)]" />

      {/* Subtle Antique Cartographic Graticule (Static Vector Lines) */}
      <svg
        className="absolute inset-0 w-full h-full opacity-[0.035]"
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
      >
        <defs>
          <pattern
            id="graticule-grid"
            width="80"
            height="80"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 80 0 L 0 0 0 80"
              fill="none"
              stroke="#EDE5D8"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#graticule-grid)" />
      </svg>
    </div>
  );
}
