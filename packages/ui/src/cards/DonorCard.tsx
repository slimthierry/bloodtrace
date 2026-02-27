import React from 'react';
import { clsx } from 'clsx';
import type { Donor } from '@bloodtrace/types';

interface DonorCardProps {
  donor: Donor;
  onClick?: () => void;
  className?: string;
}

export function DonorCard({ donor, onClick, className }: DonorCardProps) {
  return (
    <div
      onClick={onClick}
      className={clsx(
        'rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4',
        onClick && 'cursor-pointer hover:shadow-md transition-shadow',
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-gray-900 dark:text-gray-100">
            {donor.first_name} {donor.last_name}
          </h3>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
            IPP: {donor.ipp}
          </p>
        </div>
        <span className="text-xl font-bold text-brand-600 dark:text-brand-400">
          {donor.blood_type}{donor.rh_factor}
        </span>
      </div>

      <div className="mt-3 flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
        <span>{donor.donation_count} don(s)</span>
        <span className={clsx(
          'inline-flex items-center rounded-full px-2 py-0.5 font-medium',
          donor.eligibility_status === 'eligible'
            ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
            : 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400',
        )}>
          {donor.eligibility_status === 'eligible' ? 'Eligible' : 'Ajourne'}
        </span>
      </div>
    </div>
  );
}
