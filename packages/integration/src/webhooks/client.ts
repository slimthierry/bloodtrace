/**
 * Webhook client for receiving and processing BloodTrace events
 * in the parent SIH system.
 */

import type { WebhookEventType } from '@bloodtrace/types';

export { type WebhookEventType } from '@bloodtrace/types';

export interface WebhookPayload {
  event: WebhookEventType;
  timestamp: string;
  source: 'bloodtrace';
  data: Record<string, unknown>;
}

export type WebhookHandler = (payload: WebhookPayload) => void | Promise<void>;

/**
 * Webhook client for the parent SIH to receive and process BloodTrace events.
 *
 * Usage:
 * ```ts
 * const client = new WebhookClient('your-webhook-secret');
 *
 * client.on('low_stock', async (payload) => {
 *   // Handle low stock alert
 *   console.log('Low stock:', payload.data.blood_group);
 * });
 *
 * client.on('transfusion_reaction', async (payload) => {
 *   // Alert the on-call hematologist
 * });
 *
 * // In your webhook endpoint handler:
 * app.post('/webhooks/bloodtrace', (req, res) => {
 *   const signature = req.headers['x-bloodtrace-signature'];
 *   if (client.verifySignature(req.body, signature)) {
 *     client.processEvent(req.body);
 *     res.status(200).send('OK');
 *   } else {
 *     res.status(401).send('Invalid signature');
 *   }
 * });
 * ```
 */
export class WebhookClient {
  private secret: string;
  private handlers: Map<WebhookEventType | '*', WebhookHandler[]> = new Map();

  constructor(secret: string) {
    this.secret = secret;
  }

  /**
   * Register a handler for a specific event type, or '*' for all events.
   */
  on(eventType: WebhookEventType | '*', handler: WebhookHandler): void {
    const existing = this.handlers.get(eventType) || [];
    existing.push(handler);
    this.handlers.set(eventType, existing);
  }

  /**
   * Remove a handler for a specific event type.
   */
  off(eventType: WebhookEventType | '*', handler: WebhookHandler): void {
    const existing = this.handlers.get(eventType) || [];
    this.handlers.set(
      eventType,
      existing.filter((h) => h !== handler),
    );
  }

  /**
   * Verify the HMAC-SHA256 signature of a webhook payload.
   */
  async verifySignature(payload: string, signature: string): Promise<boolean> {
    if (!signature.startsWith('sha256=')) return false;
    const providedHash = signature.slice(7);

    // Use Web Crypto API for signature verification
    const encoder = new TextEncoder();
    const key = await crypto.subtle.importKey(
      'raw',
      encoder.encode(this.secret),
      { name: 'HMAC', hash: 'SHA-256' },
      false,
      ['sign'],
    );

    const signatureBuffer = await crypto.subtle.sign(
      'HMAC',
      key,
      encoder.encode(payload),
    );

    const computedHash = Array.from(new Uint8Array(signatureBuffer))
      .map((b) => b.toString(16).padStart(2, '0'))
      .join('');

    return computedHash === providedHash;
  }

  /**
   * Process a received webhook event and dispatch to registered handlers.
   */
  async processEvent(payload: WebhookPayload): Promise<void> {
    const eventHandlers = this.handlers.get(payload.event) || [];
    const wildcardHandlers = this.handlers.get('*') || [];
    const allHandlers = [...eventHandlers, ...wildcardHandlers];

    for (const handler of allHandlers) {
      try {
        await handler(payload);
      } catch (error) {
        console.error(`Webhook handler error for ${payload.event}:`, error);
      }
    }
  }
}
