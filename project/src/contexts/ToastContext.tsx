import React, { createContext, useCallback, useContext, useMemo, useState } from 'react';

export type Toast = { id: string; title?: string; message: string; type?: 'success' | 'error' | 'info' };

type ToastContextType = {
  toasts: Toast[];
  show: (message: string, opts?: Partial<Omit<Toast, 'id' | 'message'>>) => void;
  remove: (id: string) => void;
};

const ToastContext = createContext<ToastContextType | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const remove = useCallback((id: string) => {
    setToasts((t) => t.filter((x) => x.id !== id));
  }, []);

  const show = useCallback((message: string, opts?: Partial<Omit<Toast, 'id' | 'message'>>) => {
    const id = Math.random().toString(36).slice(2);
    const toast: Toast = { id, message, title: opts?.title, type: opts?.type || 'info' };
    setToasts((t) => [...t, toast]);
    setTimeout(() => remove(id), 2500);
  }, [remove]);

  const value = useMemo(() => ({ toasts, show, remove }), [toasts, show, remove]);

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="fixed bottom-4 right-4 space-y-2 z-[1000]">
        {toasts.map((t) => (
          <div key={t.id} className={`px-4 py-3 rounded-md border shadow-lg text-sm ${
            t.type === 'success' ? 'bg-emerald-900/40 border-emerald-500/30 text-emerald-200' :
            t.type === 'error' ? 'bg-red-900/40 border-red-500/30 text-red-200' :
            'bg-zinc-900/60 border-zinc-700 text-zinc-200'
          }`}>
            {t.title && <div className="font-semibold mb-0.5">{t.title}</div>}
            <div>{t.message}</div>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const ctx = useContext(ToastContext);
  if (!ctx) throw new Error('useToast must be used within ToastProvider');
  return ctx;
}
