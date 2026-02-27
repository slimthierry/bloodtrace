/**
 * Semantic color mapping utilities for BloodTrace UI.
 */

import type {
  BloodType,
  BloodGroup,
  BagStatus,
  Urgency,
  EligibilityStatus,
  ReactionType,
  BloodComponent,
} from '@bloodtrace/types';

/** Blood group display colors */
export function bloodGroupColor(group: BloodGroup | string): string {
  const type = group.replace(/[+-]$/, '');
  switch (type) {
    case 'A': return 'text-red-600 dark:text-red-400';
    case 'B': return 'text-blue-600 dark:text-blue-400';
    case 'AB': return 'text-purple-600 dark:text-purple-400';
    case 'O': return 'text-emerald-600 dark:text-emerald-400';
    default: return 'text-gray-600 dark:text-gray-400';
  }
}

/** Bag status badge classes */
export function statusColor(status: BagStatus | string): string {
  switch (status) {
    case 'available': return 'badge-status-available';
    case 'reserved': return 'badge-status-reserved';
    case 'crossmatched': return 'badge-status-reserved';
    case 'expired': return 'badge-status-expired';
    case 'quarantine': return 'badge-status-quarantine';
    case 'transfused': return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
    case 'discarded': return 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400';
    default: return 'badge-urgency-routine';
  }
}

/** Urgency badge classes */
export function urgencyColor(urgency: Urgency | string): string {
  switch (urgency) {
    case 'routine': return 'badge-urgency-routine';
    case 'urgent': return 'badge-urgency-urgent';
    case 'emergency': return 'badge-urgency-emergency';
    case 'massive': return 'badge-urgency-massive';
    default: return 'badge-urgency-routine';
  }
}

/** Component labels in French */
export function componentLabel(component: BloodComponent | string): string {
  switch (component) {
    case 'whole_blood': return 'Sang total';
    case 'packed_rbc': return 'CGR';
    case 'plasma': return 'Plasma';
    case 'platelets': return 'Plaquettes';
    case 'cryoprecipitate': return 'Cryoprecipite';
    default: return component;
  }
}

/** Status labels in French */
export function statusLabel(status: BagStatus | string): string {
  switch (status) {
    case 'available': return 'Disponible';
    case 'reserved': return 'Reserve';
    case 'crossmatched': return 'Cross-match';
    case 'transfused': return 'Transfuse';
    case 'expired': return 'Expire';
    case 'discarded': return 'Elimine';
    case 'quarantine': return 'Quarantaine';
    default: return status;
  }
}

/** Urgency labels in French */
export function urgencyLabel(urgency: Urgency | string): string {
  switch (urgency) {
    case 'routine': return 'Routine';
    case 'urgent': return 'Urgent';
    case 'emergency': return 'Urgence';
    case 'massive': return 'Massive';
    default: return urgency;
  }
}

/** Eligibility labels in French */
export function eligibilityLabel(status: EligibilityStatus | string): string {
  switch (status) {
    case 'eligible': return 'Eligible';
    case 'temporary_deferral': return 'Ajournement temporaire';
    case 'permanent_deferral': return 'Ajournement permanent';
    default: return status;
  }
}

/** Reaction labels in French */
export function reactionLabel(reaction: ReactionType | string): string {
  switch (reaction) {
    case 'none': return 'Aucune';
    case 'mild': return 'Legere';
    case 'moderate': return 'Moderee';
    case 'severe': return 'Severe';
    default: return reaction;
  }
}
