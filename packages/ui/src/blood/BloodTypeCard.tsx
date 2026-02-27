import React from 'react';
import { clsx } from 'clsx';
import type { BloodGroup } from '@bloodtrace/types';

interface BloodTypeCardProps {
  bloodGroup: BloodGroup;
  label?: string;
  count?: number;
  variant?: 'default' | 'compact';
  className?: string;
}

const GROUP_STYLES: Record<string, { bg: string; text: string; border: string }> = {
  A: { bg: 'bg-red-50 dark:bg-red-950', text: 'text-red-700 dark:text-red-300', border: 'border-red-200 dark:border-red-800' },
  B: { bg: 'bg-blue-50 dark:bg-blue-950', text: 'text-blue-700 dark:text-blue-300', border: 'border-blue-200 dark:border-blue-800' },
  AB: { bg: 'bg-purple-50 dark:bg-purple-950', text: 'text-purple-700 dark:text-purple-300', border: 'border-purple-200 dark:border-purple-800' },
  O: { bg: 'bg-emerald-50 dark:bg-emerald-950', text: 'text-emerald-700 dark:text-emerald-300', border: 'border-emerald-200 dark:border-emerald-800' },
};

export function BloodTypeCard({ bloodGroup, label, count, variant = 'default', className }: BloodTypeCardProps) {
  const type = bloodGroup.replace(/[+-]$/, '');
  const styles = GROUP_STYLES[type] || GROUP_STYLES.O;

  if (variant === 'compact') {
    return (
      <span
        className={clsx(
          'inline-flex items-center justify-center rounded-md px-2 py-1 text-sm font-bold border',
          styles.bg, styles.text, styles.border,
          className,
        )}
      >
        {bloodGroup}
      </span>
    );
  }

  return (
    <div className={clsx('rounded-xl border p-4', styles.bg, styles.border, className)}>
      <div className={clsx('text-3xl font-bold', styles.text)}>{bloodGroup}</div>
      {label && <p className="text-xs text-gray-600 dark:text-gray-400 mt-1">{label}</p>}
      {count !== undefined && (
        <p className={clsx('text-lg font-semibold mt-2', styles.text)}>{count}</p>
      )}
    </div>
  );
}
