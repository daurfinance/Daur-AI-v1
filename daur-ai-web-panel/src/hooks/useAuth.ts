import { useState, useCallback } from 'react';

// Minimal useAuth hook stub for local/autonomous mode
export function useAuth() {
  const [token] = useState<string | null>(() => {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('daur_token');
    }
    return null;
  });

  const logout = useCallback(() => {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('daur_token');
    }
  }, []);

  return { token, logout };
}
