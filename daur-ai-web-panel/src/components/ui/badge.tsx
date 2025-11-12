import React from 'react';

export interface BadgeProps {
  className?: string;
  variant?: string;
  children: React.ReactNode;
}

export const Badge: React.FC<BadgeProps> = ({ className = '', variant = 'default', children }) => (
  <span className={`inline-block px-2 py-1 rounded bg-gray-200 text-xs ${className}`} data-variant={variant}>
    {children}
  </span>
);
