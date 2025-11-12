import { useState, useCallback } from 'react';
import { useAuth } from './useAuth';
import { apiClient } from '@/lib/api';

export interface Subscription {
  id: string;
  name: string;
  price: number;
  features: string[];
}

export interface PaymentMethod {
  type: 'card' | 'paypal';
  details: any;
}

export function useSubscription() {
  const { token } = useAuth();
  const [currentPlan, setCurrentPlan] = useState<Subscription | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const fetchCurrentPlan = useCallback(async () => {
    try {
      setIsLoading(true);
      const response = await apiClient.get('/billing/subscription', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCurrentPlan(response.data);
    } catch (error) {
      console.error('Error fetching subscription:', error);
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  const subscribe = useCallback(async (planId: string, paymentMethod?: PaymentMethod) => {
    try {
      setIsLoading(true);
      await apiClient.post('/billing/subscribe', {
        planId,
        paymentMethod
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      await fetchCurrentPlan();
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Ошибка подписки');
    } finally {
      setIsLoading(false);
    }
  }, [token, fetchCurrentPlan]);

  const cancelSubscription = useCallback(async () => {
    try {
      setIsLoading(true);
      await apiClient.post('/billing/cancel', null, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setCurrentPlan(null);
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.error || 'Ошибка отмены подписки');
    } finally {
      setIsLoading(false);
    }
  }, [token]);

  return {
    currentPlan,
    isLoading,
    subscribe,
    cancelSubscription
  };
}