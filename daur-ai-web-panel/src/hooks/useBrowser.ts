
import { useState, useCallback } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '@/lib/api';

export function useBrowser() {
  const { token } = useAuth();
  const [isLoading, setIsLoading] = useState(false);

  const navigate = useCallback(async (url: string) => {
    try {
      setIsLoading(true);
      await apiClient.post('/browser/navigate', { url }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Ошибка навигации');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const click = useCallback(async (selector: string) => {
    try {
      setIsLoading(true);
      await apiClient.post('/browser/click', { selector }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Ошибка клика');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const type = useCallback(async (selector: string, text: string) => {
    try {
      setIsLoading(true);
      await apiClient.post('/browser/type', { selector, text }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Ошибка ввода текста');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const screenshot = useCallback(async (filename?: string) => {
    try {
      setIsLoading(true);
      const response = await apiClient.post('/browser/screenshot', null, {
        params: { filename },
        headers: { Authorization: `Bearer ${token}` }
      });
      return response.data.path;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Ошибка создания скриншота');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  return {
    navigate,
    click,
    type,
    screenshot,
    isLoading
  };
}
