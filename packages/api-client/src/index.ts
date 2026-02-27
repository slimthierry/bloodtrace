/**
 * @bloodtrace/api-client - HTTP client for the BloodTrace backend API.
 *
 * Provides typed methods for all API endpoints.
 */

import type {
  LoginRequest,
  TokenResponse,
  User,
  Donor,
  Donation,
  BloodBag,
  TransfusionRequest,
  Transfusion,
  AuditLog,
  StockLevel,
  DashboardStats,
  TraceabilityChain,
} from '@bloodtrace/types';

export class BloodTraceClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = '/api') {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(
    method: string,
    path: string,
    body?: unknown,
    params?: Record<string, string>,
  ): Promise<T> {
    const url = new URL(`${this.baseUrl}${path}`, window.location.origin);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value) url.searchParams.set(key, value);
      });
    }

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(url.toString(), {
      method,
      headers,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: 'Erreur inconnue' }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth
  async login(data: LoginRequest): Promise<TokenResponse> {
    return this.request('POST', '/v1/auth/login', data);
  }

  async getMe(): Promise<User> {
    return this.request('GET', '/v1/auth/me');
  }

  // Donors
  async getDonors(params?: Record<string, string>) {
    return this.request<{ donors: Donor[]; total: number; page: number; page_size: number }>(
      'GET', '/v1/donors', undefined, params,
    );
  }

  async getDonor(id: number): Promise<Donor> {
    return this.request('GET', `/v1/donors/${id}`);
  }

  async createDonor(data: Partial<Donor>): Promise<Donor> {
    return this.request('POST', '/v1/donors', data);
  }

  // Donations
  async getDonations(params?: Record<string, string>) {
    return this.request<{ donations: Donation[]; total: number; page: number; page_size: number }>(
      'GET', '/v1/donations', undefined, params,
    );
  }

  async createDonation(data: Partial<Donation>): Promise<Donation> {
    return this.request('POST', '/v1/donations', data);
  }

  // Inventory
  async getBloodBags(params?: Record<string, string>) {
    return this.request<{ blood_bags: BloodBag[]; total: number; page: number; page_size: number }>(
      'GET', '/v1/inventory', undefined, params,
    );
  }

  async getStockSummary() {
    return this.request<{ levels: StockLevel[]; total_available: number; total_expiring_soon: number; alerts: string[] }>(
      'GET', '/v1/inventory/stock',
    );
  }

  async getCompatibilityMatrix() {
    return this.request('GET', '/v1/inventory/compatibility');
  }

  async findCompatibleBags(params: Record<string, string>) {
    return this.request<{ matches: BloodBag[]; found: number; sufficient: boolean }>(
      'GET', '/v1/inventory/match', undefined, params,
    );
  }

  // Transfusions
  async getTransfusionRequests(params?: Record<string, string>) {
    return this.request<{ requests: TransfusionRequest[]; total: number; page: number; page_size: number }>(
      'GET', '/v1/transfusions/requests', undefined, params,
    );
  }

  async createTransfusionRequest(data: Partial<TransfusionRequest>): Promise<TransfusionRequest> {
    return this.request('POST', '/v1/transfusions/requests', data);
  }

  async updateTransfusionRequest(id: number, data: Partial<TransfusionRequest>): Promise<TransfusionRequest> {
    return this.request('PUT', `/v1/transfusions/requests/${id}`, data);
  }

  async getTraceabilityChain(transfusionId: number): Promise<TraceabilityChain> {
    return this.request('GET', `/v1/transfusions/${transfusionId}/trace`);
  }

  // Dashboard
  async getDashboard() {
    return this.request('GET', '/v1/dashboard');
  }

  // Audit
  async getAuditLogs(params?: Record<string, string>) {
    return this.request<{ logs: AuditLog[]; total: number; page: number; page_size: number }>(
      'GET', '/v1/audit', undefined, params,
    );
  }

  // FHIR
  async getFHIRPatient(idOrIpp: string) {
    return this.request('GET', `/fhir/Patient/${idOrIpp}`);
  }

  async getFHIRSpecimen(id: number) {
    return this.request('GET', `/fhir/Specimen/${id}`);
  }

  async getFHIRServiceRequest(id: number) {
    return this.request('GET', `/fhir/ServiceRequest/${id}`);
  }

  // Health
  async healthCheck() {
    return this.request<{ status: string; service: string; version: string }>('GET', '/health');
  }
}

export const apiClient = new BloodTraceClient();
