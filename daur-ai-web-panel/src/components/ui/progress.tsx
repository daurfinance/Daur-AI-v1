import React from 'react';

export interface ProgressProps {
  className?: string;
  value: number;
}

export const Progress: React.FC<ProgressProps> = ({ className = '', value }) => (
  <div className={`w-full h-2 bg-gray-200 rounded ${className}`}>
    <div
      className="h-2 bg-blue-500 rounded"
      style={{ width: `${value}%` }}
    />
  </div>
);
