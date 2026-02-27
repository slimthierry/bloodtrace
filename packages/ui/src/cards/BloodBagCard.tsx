import React from 'react';
import { clsx } from 'clsx';
import type { BloodBag } from '@bloodtrace/types';

interface BloodBagCardProps {
  bag: BloodBag;
  onClick?: () => void;
  className?: string;
}

const STATUS_COLORS: Record<string, string> = {
  available: 'border-l-emerald-500',
  reserved: 'border-l-amber-500',
  crossmatched: 'border-l-amber-500',
  transfused: 'border-l-blue-500',
  expired: 'border-l-red-500',
  discarded: 'border-l-gray-500',
  quarantine: 'border-l-purple-500',
};

const COMPONENT_LABELS: Record<string, string> = {
  whole_blood: 'Sang total',
  packed_rbc: 'CGR',
  plasma: 'Plasma',
  platelets: 'Plaquettes',
  cryoprecipitate: 'Cryoprecipite',
};

export function BloodBagCard({ bag, onClick, className }: BloodBagCardProps) {
  const daysUntilExpiry = Math.ceil(
    (new Date(bag.expiry_date).getTime() - Date.now()) / (1000 * 60 * 60 * 24),
  );

  return (
    <div
      onClick={onClick}
      className={clsx(
        'rounded-xl border border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 p-4 border-l-4',
        STATUS_COLORS[bag.status] || 'border-l-gray-500',
        onClick && 'cursor-pointer hover:shadow-md transition-shadow',
        className,
      )}
    >
      <div className="flex items-start justify-between">
        <div>
          <span className="text-xs text-gray-500 dark:text-gray-400">Poche #{bag.id}</span>
          <p className="text-sm font-medium text-gray-900 dark:text-gray-100 mt-0.5">
            {COMPONENT_LABELS[bag.component] || bag.component}
          </p>
        </div>
        <span className="text-xl font-bold text-brand-600 dark:text-brand-400">
          {bag.blood_type}{bag.rh_factor}
        </span>
      </div>

      <div className="mt-3 flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
        <span>{bag.volume_ml} mL</span>
        <span className={clsx(
          daysUntilExpiry <= 3 && bag.status === 'available' ? 'text-red-600 dark:text-red-400 font-medium' : '',
        )}>
          {daysUntilExpiry > 0 ? `Expire dans ${daysUntilExpiry}j` : 'Expire'}
        </span>
      </div>
    </div>
  );
}
