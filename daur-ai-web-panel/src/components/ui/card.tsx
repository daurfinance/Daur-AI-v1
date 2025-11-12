import React from 'react';

export interface CardProps {
  className?: string;
  children: React.ReactNode;
}

export const Card: React.FC<CardProps> = ({ className = '', children }) => (
  <div className={`bg-white rounded-lg shadow ${className}`}>{children}</div>
);

export const CardHeader: React.FC<CardProps> = ({ className = '', children }) => (
  <div className={`p-4 border-b ${className}`}>{children}</div>
);

export const CardTitle: React.FC<CardProps> = ({ className = '', children }) => (
  <h3 className={`text-lg font-bold ${className}`}>{children}</h3>
);

export const CardDescription: React.FC<CardProps> = ({ className = '', children }) => (
  <p className={`text-sm text-gray-500 ${className}`}>{children}</p>
);

export const CardContent: React.FC<CardProps> = ({ className = '', children }) => (
  <div className={`p-4 ${className}`}>{children}</div>
);
