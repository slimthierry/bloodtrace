import React from 'react';
import { clsx } from 'clsx';
import type { StockLevel } from '../../types';

interface StockGaugeProps {
  level: StockLevel;
  maxStock?: number;
  className?: string;
}

export function StockGauge({ level, maxStock = 50, className }: StockGaugeProps) {
  const percentage = Math.min((level.available / maxStock) * 100, 100);
  const isLow = level.available < 5;
  const isCritical = level.available === 0;

  return (
    <div className={clsx('rounded-xl border p-4 bg-white dark:bg-gray-900', isCritical && 'ring-2 ring-red-500', className)}>
      <div className="flex items-center justify-between mb-3">
        <span className="text-2xl font-bold text-brand-600 dark:text-brand-400">
          {level.blood_group}
        </span>
        {isLow && (
          <span className={clsx('text-xs font-medium', isCritical ? 'text-red-600' : 'text-amber-600')}>
            {isCritical ? 'CRITIQUE' : 'BAS'}
          </span>
        )}
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-2">
        <div
          className={clsx(
            'h-3 rounded-full transition-all duration-500',
            isCritical ? 'bg-red-600' : isLow ? 'bg-amber-500' : 'bg-brand-500',
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{level.available} disp.</span>
        <span>{level.reserved} res.</span>
      </div>

      {level.expiring_soon > 0 && (
        <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
          {level.expiring_soon} expirant bientot
        </p>
      )}
    </div>
  );
}
