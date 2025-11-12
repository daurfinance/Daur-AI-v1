import React from 'react';
import { useUser } from '@/hooks/useUser';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Icons } from '@/components/icons';

export function UserProfile() {
  const { user, logout } = useUser();

  if (!user) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Профиль пользователя</CardTitle>
        <CardDescription>Управление вашей учетной записью</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="rounded-full bg-gray-200 p-2">
              <Icons.user className="h-6 w-6" />
            </div>
            <div>
              <h3 className="font-medium">{user.username}</h3>
              <p className="text-sm text-gray-500">{user.email}</p>
            </div>
          </div>
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Подписка</h4>
            <div className="flex items-center justify-between">
              <span>{user.subscription?.tier || 'Free'}</span>
              <Button variant="outline" size="sm">
                Изменить план
              </Button>
            </div>
          </div>
          <div className="space-y-2">
            <h4 className="text-sm font-medium">Использование</h4>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span className="text-sm">Запросы</span>
                <span className="text-sm font-medium">
                  {user.usage?.requests_today} / {user.usage?.daily_limit}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm">Хранилище</span>
                <span className="text-sm font-medium">
                  {(user.usage?.storage_used / 1024).toFixed(2)} GB
                </span>
              </div>
            </div>
          </div>
          <Button variant="destructive" onClick={logout} className="w-full">
            Выйти
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}