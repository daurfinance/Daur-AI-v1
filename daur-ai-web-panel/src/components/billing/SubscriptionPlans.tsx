import React from 'react';
import { useSubscription } from '@/hooks/useSubscription';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Icons } from '@/components/icons';
import { Badge } from '@/components/ui/badge';

const plans = [
	{
		id: 'free',
		name: 'Free',
		price: 0,
		features: [
			'До 100 запросов в день',
			'100 MB хранилища',
			'Базовые плагины',
			'Стандартная поддержка',
		],
	},
	{
		id: 'basic',
		name: 'Basic',
		price: 9.99,
		features: [
			'До 1000 запросов в день',
			'1 GB хранилища',
			'Все плагины',
			'Стандартная поддержка',
		],
	},
	{
		id: 'pro',
		name: 'Professional',
		price: 29.99,
		features: [
			'До 10000 запросов в день',
			'10 GB хранилища',
			'Все плагины',
			'Приоритетная поддержка',
		],
	},
	{
		id: 'enterprise',
		name: 'Enterprise',
		price: 99.99,
		features: [
			'Неограниченные запросы',
			'Неограниченное хранилище',
			'Все плагины',
			'Персональная поддержка 24/7',
		],
	},
];

export function SubscriptionPlans() {
	const { currentPlan, subscribe, isLoading } = useSubscription();

	return (
		<div className="space-y-8">
			<div>
				<h2 className="text-2xl font-bold">Тарифные планы</h2>
				<p className="text-gray-500">
					Выберите план, который подходит вашим потребностям
				</p>
			</div>

			<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
				{plans.map((plan) => (
					<Card
						key={plan.id}
						className={`relative ${
							currentPlan?.id === plan.id ? 'border-primary' : ''
						}`}
					>
						{currentPlan?.id === plan.id && (
							<Badge
								className="absolute -top-2 -right-2"
								variant="default"
							>
								Текущий план
							</Badge>
						)}
						<CardHeader>
							<CardTitle>{plan.name}</CardTitle>
							<CardDescription>
								<span className="text-2xl font-bold">
									${plan.price}
								</span>
								/месяц
							</CardDescription>
						</CardHeader>
						<CardContent>
							<ul className="space-y-2">
								{plan.features.map((feature, index) => (
									<li
										key={index}
										className="flex items-center space-x-2"
									>
										<Icons.check className="h-4 w-4 text-green-500" />
										<span>{feature}</span>
									</li>
								))}
							</ul>
							<Button
								className="w-full mt-4"
								variant={
									currentPlan?.id === plan.id
										? 'outline'
										: 'default'
								}
								disabled={isLoading || currentPlan?.id === plan.id}
								onClick={() => subscribe(plan.id)}
							>
								{currentPlan?.id === plan.id
									? 'Текущий план'
									: 'Выбрать план'}
							</Button>
						</CardContent>
					</Card>
				))}
			</div>

			<div className="text-center text-sm text-gray-500">
				<p>
					Цены указаны без учета НДС. Возможна ежегодная оплата со скидкой
					20%.
				</p>
				<p>Для корпоративных клиентов доступны индивидуальные условия.</p>
			</div>
		</div>
	);
}