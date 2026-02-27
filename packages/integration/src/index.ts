/**
 * @bloodtrace/integration - SIH Integration utilities
 *
 * Provides FHIR resource builders and webhook event handling
 * for integrating BloodTrace into a Hospital Information System.
 */

export { buildFHIRPatient, buildFHIRPatientFromDonor } from './fhir/patient';
export { buildFHIRSpecimen, buildFHIRSpecimenFromBloodBag } from './fhir/specimen';
export {
  WebhookEventType,
  type WebhookPayload,
  type WebhookHandler,
  WebhookClient,
} from './webhooks/client';
export {
  createLowStockEvent,
  createExpiringBloodEvent,
  createTransfusionReactionEvent,
} from './webhooks/events';
