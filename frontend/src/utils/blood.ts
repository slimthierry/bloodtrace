/**
 * Blood compatibility utilities implementing ABO+Rh system rules.
 *
 * - O- is universal donor for RBC
 * - AB+ is universal recipient for RBC
 * - For plasma, rules are inverted
 */

import type { BloodType, RhFactor, BloodGroup } from '../types';

/** RBC compatibility: recipient -> compatible donors */
export const RBC_COMPATIBILITY: Record<BloodGroup, BloodGroup[]> = {
  'O-':  ['O-'],
  'O+':  ['O-', 'O+'],
  'A-':  ['O-', 'A-'],
  'A+':  ['O-', 'O+', 'A-', 'A+'],
  'B-':  ['O-', 'B-'],
  'B+':  ['O-', 'O+', 'B-', 'B+'],
  'AB-': ['O-', 'A-', 'B-', 'AB-'],
  'AB+': ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
};

/** Plasma compatibility: recipient -> compatible donors */
export const PLASMA_COMPATIBILITY: Record<BloodGroup, BloodGroup[]> = {
  'O-':  ['O-', 'O+', 'A-', 'A+', 'B-', 'B+', 'AB-', 'AB+'],
  'O+':  ['O+', 'A+', 'B+', 'AB+'],
  'A-':  ['A-', 'A+', 'AB-', 'AB+'],
  'A+':  ['A+', 'AB+'],
  'B-':  ['B-', 'B+', 'AB-', 'AB+'],
  'B+':  ['B+', 'AB+'],
  'AB-': ['AB-', 'AB+'],
  'AB+': ['AB+'],
};

export function toBloodGroup(bloodType: BloodType, rh: RhFactor): BloodGroup {
  return `${bloodType}${rh}` as BloodGroup;
}

export function isRBCCompatible(
  donorType: BloodType,
  donorRh: RhFactor,
  recipientType: BloodType,
  recipientRh: RhFactor,
): boolean {
  const donorGroup = toBloodGroup(donorType, donorRh);
  const recipientGroup = toBloodGroup(recipientType, recipientRh);
  return RBC_COMPATIBILITY[recipientGroup]?.includes(donorGroup) ?? false;
}

export function isPlasmaCompatible(
  donorType: BloodType,
  donorRh: RhFactor,
  recipientType: BloodType,
  recipientRh: RhFactor,
): boolean {
  const donorGroup = toBloodGroup(donorType, donorRh);
  const recipientGroup = toBloodGroup(recipientType, recipientRh);
  return PLASMA_COMPATIBILITY[recipientGroup]?.includes(donorGroup) ?? false;
}

export function getCompatibleDonors(
  recipientType: BloodType,
  recipientRh: RhFactor,
  component: 'rbc' | 'plasma' = 'rbc',
): BloodGroup[] {
  const recipientGroup = toBloodGroup(recipientType, recipientRh);
  if (component === 'plasma') {
    return PLASMA_COMPATIBILITY[recipientGroup] ?? [];
  }
  return RBC_COMPATIBILITY[recipientGroup] ?? [];
}
