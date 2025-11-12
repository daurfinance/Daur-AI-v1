import { useState, useEffect, useCallback } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '@/lib/api';

export interface Plugin {
  id: string;
  name: string;
  description: string;
  version: string;
  price: number;
  tags: string[];
  downloads: number;
}

export function usePlugins() {
  const { token } = useAuth();
  const [plugins, setPlugins] = useState<Plugin[]>([]);
  const [installedPlugins, setInstalledPlugins] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPlugins = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get('/plugins/marketplace', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlugins(response.data);
      
      const installed = await apiClient.get('/plugins', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInstalledPlugins(installed.data.map((p: Plugin) => p.id));
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const searchPlugins = useCallback(async (query: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      const response = await apiClient.get('/plugins/marketplace', {
        params: { q: query },
        headers: { Authorization: `Bearer ${token}` }
      });
      setPlugins(response.data);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const installPlugin = useCallback(async (pluginId: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      await apiClient.post(`/plugins/install/${pluginId}`, null, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setInstalledPlugins(prev => [...prev, pluginId]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  useEffect(() => {
    fetchPlugins();
  }, [fetchPlugins]);

  return {
    plugins,
    installedPlugins,
    isLoading,
    error,
    searchPlugins,
    installPlugin
  };
}