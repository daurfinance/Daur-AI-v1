import React from 'react';

export interface ButtonProps {
  className?: string;
  variant?: string;
  size?: string;
  asChild?: boolean;
  children: React.ReactNode;
  onClick?: React.MouseEventHandler<HTMLButtonElement>;
  disabled?: boolean;
}

export const Button: React.FC<ButtonProps> = ({ className = '', variant = 'default', size = 'md', asChild = false, children, onClick, disabled }) => (
  <button
    className={`px-4 py-2 rounded ${className}`}
    data-variant={variant}
    data-size={size}
    onClick={onClick}
    disabled={disabled}
  >
    {children}
  </button>
);
