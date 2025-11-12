import React from 'react';
import { usePlugins } from '@/hooks/usePlugins';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Search } from '@/components/ui/search';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';

export function PluginMarketplace() {
  const {
    plugins,
    installedPlugins,
    searchPlugins,
    installPlugin,
    isLoading,
    error
  } = usePlugins();

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Маркетплейс плагинов</h2>
        <Search
          placeholder="Поиск плагинов..."
          onChange={(e) => searchPlugins(e.target.value)}
        />
      </div>

      {error && (
        <div className="p-4 bg-red-50 text-red-600 rounded-lg">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {isLoading ? (
          Array(6).fill(0).map((_, i) => (
            <Card key={i}>
              <CardHeader>
                <Skeleton className="h-6 w-3/4" />
                <Skeleton className="h-4 w-1/2" />
              </CardHeader>
              <CardContent>
                <Skeleton className="h-20 w-full" />
                <Skeleton className="h-8 w-24 mt-4" />
              </CardContent>
            </Card>
          ))
        ) : (
          plugins.map((plugin) => (
            <Card key={plugin.id}>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  {plugin.name}
                  <Badge variant={plugin.price === 0 ? "secondary" : "default"}>
                    {plugin.price === 0 ? "Free" : `$${plugin.price}`}
                  </Badge>
                </CardTitle>
                <CardDescription>{plugin.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="flex flex-wrap gap-2">
                    {plugin.tags?.map((tag) => (
                      <Badge key={tag} variant="outline">
                        {tag}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between">
                    <div className="text-sm text-gray-500">
                      v{plugin.version} • {plugin.downloads} загрузок
                    </div>
                    <Button
                      variant={installedPlugins.includes(plugin.id) ? "outline" : "default"}
                      onClick={() => installPlugin(plugin.id)}
                      disabled={installedPlugins.includes(plugin.id)}
                    >
                      {installedPlugins.includes(plugin.id) ? "Установлен" : "Установить"}
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))
        )}
      </div>
    </div>
  );
}