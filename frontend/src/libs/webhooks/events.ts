/**
 * Webhook event factory functions for SIH integration.
 */

import type { WebhookEventType } from '../../types';

export interface WebhookEventData {
  event: WebhookEventType;
  timestamp: string;
  source: 'bloodtrace';
  data: Record<string, unknown>;
}

export function createLowStockEvent(params: {
  bloodGroup: string;
  availableCount: number;
  threshold: number;
}): WebhookEventData {
  return {
    event: 'low_stock',
    timestamp: new Date().toISOString(),
    source: 'bloodtrace',
    data: {
      blood_group: params.bloodGroup,
      available_count: params.availableCount,
      threshold: params.threshold,
      severity: params.availableCount === 0 ? 'critical' : 'warning',
    },
  };
}

export function createExpiringBloodEvent(params: {
  bloodBagId: number;
  bloodGroup: string;
  expiryDate: string;
  daysRemaining: number;
}): WebhookEventData {
  return {
    event: 'expiring_blood',
    timestamp: new Date().toISOString(),
    source: 'bloodtrace',
    data: {
      blood_bag_id: params.bloodBagId,
      blood_group: params.bloodGroup,
      expiry_date: params.expiryDate,
      days_remaining: params.daysRemaining,
    },
  };
}

export function createTransfusionReactionEvent(params: {
  transfusionId: number;
  patientIpp: string;
  reactionType: string;
  reactionDetails?: string;
}): WebhookEventData {
  return {
    event: 'transfusion_reaction',
    timestamp: new Date().toISOString(),
    source: 'bloodtrace',
    data: {
      transfusion_id: params.transfusionId,
      patient_ipp: params.patientIpp,
      reaction_type: params.reactionType,
      reaction_details: params.reactionDetails,
      severity: params.reactionType === 'severe' ? 'critical' : 'warning',
    },
  };
}
