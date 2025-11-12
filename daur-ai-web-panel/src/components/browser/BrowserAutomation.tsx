import React from 'react';
import { useBrowser } from '@/hooks/useBrowser';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { useToast } from '@/hooks/useToast';

export function BrowserAutomation() {
  const { navigate, click, type, screenshot, isLoading } = useBrowser();
  const { toast } = useToast();
  const [url, setUrl] = React.useState('');
  const [selector, setSelector] = React.useState('');
  const [text, setText] = React.useState('');

  const handleNavigate = async () => {
    try {
      await navigate(url);
      toast({
        title: 'Успешно',
        description: 'Переход выполнен',
        variant: 'default',
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleClick = async () => {
    try {
      await click(selector);
      toast({
        title: 'Успешно',
        description: 'Клик выполнен',
        variant: 'default',
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleType = async () => {
    try {
      await type(selector, text);
      toast({
        title: 'Успешно',
        description: 'Текст введен',
        variant: 'default',
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  const handleScreenshot = async () => {
    try {
      const path = await screenshot();
      toast({
        title: 'Успешно',
        description: `Скриншот сохранен: ${path}`,
        variant: 'default',
      });
    } catch (error) {
      toast({
        title: 'Ошибка',
        description: error.message,
        variant: 'destructive',
      });
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Браузерная автоматизация</CardTitle>
        <CardDescription>Управление браузером через Playwright</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="navigate">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="navigate">Навигация</TabsTrigger>
            <TabsTrigger value="click">Клик</TabsTrigger>
            <TabsTrigger value="type">Ввод текста</TabsTrigger>
            <TabsTrigger value="screenshot">Скриншот</TabsTrigger>
          </TabsList>

          <TabsContent value="navigate" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="url">URL</Label>
              <div className="flex space-x-2">
                <Input
                  id="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
                <Button onClick={handleNavigate} disabled={isLoading || !url}>
                  Перейти
                </Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="click" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="click-selector">CSS селектор</Label>
              <div className="flex space-x-2">
                <Input
                  id="click-selector"
                  placeholder="#button"
                  value={selector}
                  onChange={(e) => setSelector(e.target.value)}
                />
                <Button onClick={handleClick} disabled={isLoading || !selector}>
                  Кликнуть
                </Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="type" className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="type-selector">CSS селектор</Label>
              <Input
                id="type-selector"
                placeholder="#input"
                value={selector}
                onChange={(e) => setSelector(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="type-text">Текст</Label>
              <div className="flex space-x-2">
                <Input
                  id="type-text"
                  placeholder="Текст для ввода"
                  value={text}
                  onChange={(e) => setText(e.target.value)}
                />
                <Button 
                  onClick={handleType}
                  disabled={isLoading || !selector || !text}
                >
                  Ввести
                </Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="screenshot" className="space-y-4">
            <Button
              onClick={handleScreenshot}
              disabled={isLoading}
              className="w-full"
            >
              Сделать скриншот
            </Button>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}