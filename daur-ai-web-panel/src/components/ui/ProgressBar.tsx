import React from 'react';
import { Progress } from "@/components/ui/progress"

export interface ProgressBarProps {
  value: number;
  max: number;
  label?: string;
  showPercentage?: boolean;
  className?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max,
  label,
  showPercentage = true,
  className = '',
}) => {
  const percentage = Math.round((value / max) * 100);

  return (
    <div className={`w-full ${className}`}>
      {label && (
        <div className="flex justify-between mb-1">
          <span className="text-sm font-medium">{label}</span>
          {showPercentage && <span className="text-sm font-medium">{percentage}%</span>}
        </div>
      )}
      <Progress value={percentage} />
    </div>
  );
};