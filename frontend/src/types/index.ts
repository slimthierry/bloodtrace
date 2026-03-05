/**
 * @bloodtrace/types - Shared TypeScript types for BloodTrace
 *
 * All types mirror the backend Python models and schemas.
 */

// --- Enums ---

export type BloodType = 'A' | 'B' | 'AB' | 'O';
export type RhFactor = '+' | '-';
export type BloodGroup = `${BloodType}${RhFactor}`;

export type UserRole = 'admin' | 'medecin' | 'infirmier' | 'technicien_labo' | 'efs_agent';

export type EligibilityStatus = 'eligible' | 'temporary_deferral' | 'permanent_deferral';

export type ScreeningStatus = 'pending' | 'passed' | 'failed';

export type BloodComponent = 'whole_blood' | 'packed_rbc' | 'plasma' | 'platelets' | 'cryoprecipitate';

export type BagStatus = 'available' | 'reserved' | 'crossmatched' | 'transfused' | 'expired' | 'discarded' | 'quarantine';

export type Urgency = 'routine' | 'urgent' | 'emergency' | 'massive';

export type RequestStatus = 'pending' | 'approved' | 'in_progress' | 'completed' | 'cancelled';

export type ReactionType = 'none' | 'mild' | 'moderate' | 'severe';

export type AuditAction = 'create' | 'read' | 'update' | 'delete';

// --- Models ---

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  service?: string;
  is_active: boolean;
  created_at: string;
}

export interface Donor {
  id: number;
  ipp: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  blood_type: BloodType;
  rh_factor: RhFactor;
  last_donation_date?: string;
  eligibility_status: EligibilityStatus;
  deferral_reason?: string;
  deferral_until?: string;
  donation_count: number;
  phone?: string;
  email?: string;
  created_at: string;
}

export interface Donation {
  id: number;
  donor_id: number;
  date: string;
  volume_ml: number;
  collection_site: string;
  collector_id: number;
  screening_status: ScreeningStatus;
  notes?: string;
  created_at: string;
}

export interface BloodBag {
  id: number;
  donation_id: number;
  blood_type: BloodType;
  rh_factor: RhFactor;
  component: BloodComponent;
  volume_ml: number;
  collection_date: string;
  expiry_date: string;
  status: BagStatus;
  storage_location?: string;
  storage_temperature?: number;
  created_at: string;
}

export interface TransfusionRequest {
  id: number;
  patient_ipp: string;
  patient_name: string;
  requesting_doctor_id: number;
  blood_type_needed: BloodType;
  rh_needed: RhFactor;
  component_needed: BloodComponent;
  units_needed: number;
  urgency: Urgency;
  clinical_indication: string;
  status: RequestStatus;
  created_at: string;
}

export interface Transfusion {
  id: number;
  request_id: number;
  blood_bag_id: number;
  patient_ipp: string;
  administering_nurse_id: number;
  started_at: string;
  completed_at?: string;
  reaction_type: ReactionType;
  reaction_details?: string;
  vital_signs_pre?: Record<string, unknown>;
  vital_signs_post?: Record<string, unknown>;
  created_at: string;
}

export interface AuditLog {
  id: number;
  user_id?: number;
  user_name?: string;
  action: AuditAction;
  entity_type: string;
  entity_id?: string;
  details: Record<string, unknown>;
  ip_address?: string;
  timestamp: string;
}

// --- API Response Types ---

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface StockLevel {
  blood_type: BloodType;
  rh_factor: RhFactor;
  blood_group: BloodGroup;
  available: number;
  reserved: number;
  expiring_soon: number;
  total: number;
}

export interface DashboardStats {
  total_donors: number;
  total_donations_this_month: number;
  total_transfusions_this_month: number;
  total_blood_bags_available: number;
  total_pending_requests: number;
  reactions_this_month: number;
}

export interface TraceabilityChain {
  donor_ipp: string;
  donor_name: string;
  donor_blood_group: BloodGroup;
  donation_id: number;
  donation_date: string;
  blood_bag_id: number;
  blood_bag_component: BloodComponent;
  transfusion_id: number;
  patient_ipp: string;
  patient_name: string;
  transfusion_date: string;
  reaction_type: ReactionType;
}

// --- Webhook Events ---

export type WebhookEventType = 'low_stock' | 'expiring_blood' | 'transfusion_reaction';

export interface WebhookEvent {
  event: WebhookEventType;
  timestamp: string;
  source: 'bloodtrace';
  data: Record<string, unknown>;
}

// --- Auth ---

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: 'bearer';
  user_id: number;
  email: string;
  name: string;
  role: UserRole;
}

// --- Constants ---

export const ALL_BLOOD_GROUPS: BloodGroup[] = [
  'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-',
];

export const ALL_BLOOD_TYPES: BloodType[] = ['A', 'B', 'AB', 'O'];
export const ALL_RH_FACTORS: RhFactor[] = ['+', '-'];
export const ALL_COMPONENTS: BloodComponent[] = [
  'whole_blood', 'packed_rbc', 'plasma', 'platelets', 'cryoprecipitate',
];
