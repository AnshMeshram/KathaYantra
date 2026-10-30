"use client";

import { useEffect, useState } from "react";

export function AtmosphericBackground() {
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    setReducedMotion(media.matches);

    const listener = (e: MediaQueryListEvent) => setReducedMotion(e.matches);
    media.addEventListener("change", listener);
    return () => media.removeEventListener("change", listener);
  }, []);

  return (
    <div
      className="fixed inset-0 pointer-events-none z-0 overflow-hidden"
      aria-hidden="true"
    >
      {/* Candlelit Vignette Gradient */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_0%,rgba(37,24,32,0.35)_0%,transparent_70%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_15%_85%,rgba(25,17,25,0.45)_0%,transparent_60%)]" />

      {/* Floating subtle ember particles (disabled if reduced motion) */}
      {!reducedMotion && (
        <div className="absolute inset-0 opacity-20">
          <div className="absolute top-1/4 left-1/6 w-1 h-1 rounded-full bg-gold animate-pulse" />
          <div className="absolute top-2/3 left-1/3 w-1.5 h-1.5 rounded-full bg-ember animate-ping [animation-duration:4s]" />
          <div className="absolute top-1/3 right-1/4 w-1 h-1 rounded-full bg-gold animate-pulse [animation-duration:3s]" />
          <div className="absolute bottom-1/4 right-1/6 w-1.5 h-1.5 rounded-full bg-spectral animate-pulse [animation-duration:5s]" />
        </div>
      )}
    </div>
  );
}
