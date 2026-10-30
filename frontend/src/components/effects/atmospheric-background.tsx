"use client";

export function AtmosphericBackground() {
  return (
    <div
      className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      aria-hidden="true"
    >
      {/* Soft Washi Paper Tone Variations */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_15%_15%,rgba(250,244,236,0.9)_0%,transparent_60%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_85%_85%,rgba(237,226,208,0.7)_0%,transparent_65%)]" />

      {/* Subtle Antique Cartographic Graticule (Static Vector Lines) */}
      <svg
        className="absolute inset-0 w-full h-full opacity-[0.03]"
        xmlns="http://www.w3.org/2000/svg"
        width="100%"
        height="100%"
      >
        <defs>
          <pattern
            id="archival-grid"
            width="60"
            height="60"
            patternUnits="userSpaceOnUse"
          >
            <path
              d="M 60 0 L 0 0 0 60"
              fill="none"
              stroke="#70191D"
              strokeWidth="0.5"
            />
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#archival-grid)" />
      </svg>
    </div>
  );
}
