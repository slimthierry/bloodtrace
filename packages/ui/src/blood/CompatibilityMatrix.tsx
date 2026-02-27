import React from 'react';
import { clsx } from 'clsx';
import type { BloodGroup } from '@bloodtrace/types';
import { RBC_COMPATIBILITY } from '@bloodtrace/utils';

interface CompatibilityMatrixProps {
  type?: 'rbc' | 'plasma';
  className?: string;
}

const ALL_GROUPS: BloodGroup[] = ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'];

export function CompatibilityMatrix({ type = 'rbc', className }: CompatibilityMatrixProps) {
  const matrix = RBC_COMPATIBILITY; // Uses RBC by default

  return (
    <div className={clsx('overflow-x-auto', className)}>
      <h3 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
        Matrice de compatibilite {type === 'rbc' ? 'CGR' : 'Plasma'}
      </h3>
      <table className="text-xs">
        <thead>
          <tr>
            <th className="px-2 py-1 text-gray-500 dark:text-gray-400">Receveur \ Donneur</th>
            {ALL_GROUPS.map((group) => (
              <th key={group} className="px-2 py-1 text-center font-bold text-brand-600 dark:text-brand-400">
                {group}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {ALL_GROUPS.map((recipient) => (
            <tr key={recipient}>
              <td className="px-2 py-1 font-bold text-brand-600 dark:text-brand-400">{recipient}</td>
              {ALL_GROUPS.map((donor) => {
                const compatible = matrix[recipient]?.includes(donor) ?? false;
                return (
                  <td key={donor} className="px-2 py-1 text-center">
                    <span
                      className={clsx(
                        'inline-block w-5 h-5 rounded-full leading-5 text-center text-[10px] font-bold',
                        compatible
                          ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400'
                          : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
                      )}
                    >
                      {compatible ? 'O' : 'X'}
                    </span>
                  </td>
                );
              })}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
