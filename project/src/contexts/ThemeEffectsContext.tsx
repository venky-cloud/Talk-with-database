import React, { createContext, useContext, useEffect, useMemo, useState } from 'react';

type SnowMode = 'auto' | 'on' | 'off';

type ThemeEffectsContextType = {
  snowMode: SnowMode;
  setSnowMode: (m: SnowMode) => void;
  isMobile: boolean;
  shouldSnow: boolean;
  densityMobile: number;
  setDensityMobile: (n: number) => void;
  densityDesktop: number;
  setDensityDesktop: (n: number) => void;
};

const ThemeEffectsContext = createContext<ThemeEffectsContextType | undefined>(undefined);

export function ThemeEffectsProvider({ children }: { children: React.ReactNode }) {
  const [snowMode, setSnowMode] = useState<SnowMode>(() => {
    const saved = localStorage.getItem('snowMode');
    return (saved as SnowMode) || 'on';
  });

  const [isMobile, setIsMobile] = useState<boolean>(false);
  const [densityMobile, setDensityMobile] = useState<number>(() => {
    const saved = localStorage.getItem('snowDensityMobile');
    return saved ? parseInt(saved, 10) : 6;
  });
  const [densityDesktop, setDensityDesktop] = useState<number>(() => {
    const saved = localStorage.getItem('snowDensityDesktop');
    return saved ? parseInt(saved, 10) : 12;
  });

  useEffect(() => {
    try {
      const mq = window.matchMedia('(max-width: 640px)');
      const update = () => setIsMobile(mq.matches);
      update();
      mq.addEventListener?.('change', update);
      return () => mq.removeEventListener?.('change', update);
    } catch {}
  }, []);

  useEffect(() => {
    localStorage.setItem('snowMode', snowMode);
  }, [snowMode]);

  useEffect(() => {
    localStorage.setItem('snowDensityMobile', String(densityMobile));
  }, [densityMobile]);

  useEffect(() => {
    localStorage.setItem('snowDensityDesktop', String(densityDesktop));
  }, [densityDesktop]);

  const shouldSnow = useMemo(() => {
    if (snowMode === 'on') return true;
    if (snowMode === 'off') return false;
    // 'auto' => force enabled for now so effect is visible everywhere
    return true;
  }, [snowMode]);

  const value = useMemo(() => ({
    snowMode,
    setSnowMode,
    isMobile,
    shouldSnow,
    densityMobile,
    setDensityMobile,
    densityDesktop,
    setDensityDesktop,
  }), [snowMode, isMobile, shouldSnow, densityMobile, densityDesktop]);

  return (
    <ThemeEffectsContext.Provider value={value}>{children}</ThemeEffectsContext.Provider>
  );
}

export function useThemeEffects() {
  const ctx = useContext(ThemeEffectsContext);
  if (!ctx) throw new Error('useThemeEffects must be used within ThemeEffectsProvider');
  return ctx;
}
