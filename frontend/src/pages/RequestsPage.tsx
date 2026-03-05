import { useState, useEffect, type FormEvent } from 'react';
import { FileText, Plus, X, CheckCircle, XCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { clsx } from 'clsx';

interface TransfusionRequest {
  id: number;
  patient_ipp: string;
  patient_name: string;
  requesting_doctor_id: number;
  blood_type_needed: string;
  rh_needed: string;
  component_needed: string;
  units_needed: number;
  urgency: string;
  clinical_indication: string;
  status: string;
  created_at: string;
}

const STATUS_BADGES: Record<string, string> = {
  pending: 'badge-urgency-routine',
  approved: 'badge-status-available',
  in_progress: 'badge-status-reserved',
  completed: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  cancelled: 'badge-status-expired',
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'En attente',
  approved: 'Approuvee',
  in_progress: 'En cours',
  completed: 'Terminee',
  cancelled: 'Annulee',
};

const URGENCY_BADGES: Record<string, string> = {
  routine: 'badge-urgency-routine',
  urgent: 'badge-urgency-urgent',
  emergency: 'badge-urgency-emergency',
  massive: 'badge-urgency-massive',
};

const COMPONENT_LABELS: Record<string, string> = {
  whole_blood: 'Sang total',
  packed_rbc: 'CGR',
  plasma: 'Plasma',
  platelets: 'Plaquettes',
  cryoprecipitate: 'Cryoprecipite',
};

export function RequestsPage() {
  const { token, user } = useAuth();
  const [requests, setRequests] = useState<TransfusionRequest[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [statusFilter, setStatusFilter] = useState('');
  const [loading, setLoading] = useState(true);

  const fetchRequests = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: '20' });
      if (statusFilter) params.set('status', statusFilter);

      const response = await fetch(`/api/v1/transfusions/requests?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setRequests(data.requests);
        setTotal(data.total);
      }
    } catch {
      // Handle silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequests();
  }, [page, statusFilter, token]);

  const handleCreate = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);

    try {
      const response = await fetch('/api/v1/transfusions/requests', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          patient_ipp: formData.get('patient_ipp'),
          patient_name: formData.get('patient_name'),
          blood_type_needed: formData.get('blood_type_needed'),
          rh_needed: formData.get('rh_needed'),
          component_needed: formData.get('component_needed'),
          units_needed: parseInt(formData.get('units_needed') as string),
          urgency: formData.get('urgency'),
          clinical_indication: formData.get('clinical_indication'),
        }),
      });

      if (response.ok) {
        setShowForm(false);
        fetchRequests();
      }
    } catch {
      // Handle silently
    }
  };

  const handleStatusUpdate = async (requestId: number, newStatus: string) => {
    try {
      await fetch(`/api/v1/transfusions/requests/${requestId}`, {
        method: 'PUT',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: newStatus }),
      });
      fetchRequests();
    } catch {
      // Handle silently
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)] flex items-center gap-2">
            <FileText className="h-6 w-6 text-brand-500" />
            Demandes de transfusion
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            {total} demandes
          </p>
        </div>
        {(user?.role === 'admin' || user?.role === 'medecin') && (
          <button onClick={() => setShowForm(!showForm)} className="btn-primary">
            <Plus className="h-4 w-4 mr-2" />
            Nouvelle demande
          </button>
        )}
      </div>

      {/* Create form */}
      {showForm && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
              Nouvelle demande de transfusion
            </h2>
            <button onClick={() => setShowForm(false)} className="text-[var(--color-text-secondary)]">
              <X className="h-5 w-5" />
            </button>
          </div>
          <form onSubmit={handleCreate} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">IPP Patient</label>
              <input name="patient_ipp" className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Nom du patient</label>
              <input name="patient_name" className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Groupe requis</label>
              <select name="blood_type_needed" className="input-field" required>
                <option value="">Selectionner</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="AB">AB</option>
                <option value="O">O</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Rhesus requis</label>
              <select name="rh_needed" className="input-field" required>
                <option value="">Selectionner</option>
                <option value="+">+</option>
                <option value="-">-</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Composant</label>
              <select name="component_needed" className="input-field" required>
                <option value="">Selectionner</option>
                <option value="packed_rbc">CGR</option>
                <option value="plasma">Plasma</option>
                <option value="platelets">Plaquettes</option>
                <option value="whole_blood">Sang total</option>
                <option value="cryoprecipitate">Cryoprecipite</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Unites</label>
              <input name="units_needed" type="number" min="1" className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Urgence</label>
              <select name="urgency" className="input-field" required>
                <option value="routine">Routine</option>
                <option value="urgent">Urgent</option>
                <option value="emergency">Urgence</option>
                <option value="massive">Massive</option>
              </select>
            </div>
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Indication clinique</label>
              <input name="clinical_indication" className="input-field" required />
            </div>
            <div className="flex items-end">
              <button type="submit" className="btn-primary w-full">Creer la demande</button>
            </div>
          </form>
        </div>
      )}

      {/* Filter */}
      <div className="flex gap-3">
        <select
          value={statusFilter}
          onChange={(e) => { setStatusFilter(e.target.value); setPage(1); }}
          className="input-field w-auto"
        >
          <option value="">Tous les statuts</option>
          <option value="pending">En attente</option>
          <option value="approved">Approuvee</option>
          <option value="in_progress">En cours</option>
          <option value="completed">Terminee</option>
          <option value="cancelled">Annulee</option>
        </select>
      </div>

      {/* Requests table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">Patient</th>
                <th className="px-5 py-3 font-medium">Groupe</th>
                <th className="px-5 py-3 font-medium">Composant</th>
                <th className="px-5 py-3 font-medium">Unites</th>
                <th className="px-5 py-3 font-medium">Urgence</th>
                <th className="px-5 py-3 font-medium">Statut</th>
                <th className="px-5 py-3 font-medium">Date</th>
                <th className="px-5 py-3 font-medium">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {loading ? (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-brand-500 border-t-transparent mx-auto" />
                  </td>
                </tr>
              ) : requests.length === 0 ? (
                <tr>
                  <td colSpan={9} className="px-5 py-8 text-center text-[var(--color-text-secondary)]">
                    Aucune demande trouvee
                  </td>
                </tr>
              ) : (
                requests.map((req) => (
                  <tr key={req.id} className="hover:bg-[var(--color-bg-secondary)] transition-colors">
                    <td className="px-5 py-3 font-mono text-xs">#{req.id}</td>
                    <td className="px-5 py-3">
                      <div className="font-medium text-[var(--color-text-primary)]">{req.patient_name}</div>
                      <div className="text-xs text-[var(--color-text-secondary)]">IPP: {req.patient_ipp}</div>
                    </td>
                    <td className="px-5 py-3 font-bold text-brand-600 dark:text-brand-400">
                      {req.blood_type_needed}{req.rh_needed}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {COMPONENT_LABELS[req.component_needed] || req.component_needed}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">{req.units_needed}</td>
                    <td className="px-5 py-3">
                      <span className={clsx('badge', URGENCY_BADGES[req.urgency])}>
                        {req.urgency}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={clsx('badge', STATUS_BADGES[req.status])}>
                        {STATUS_LABELS[req.status] || req.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {new Date(req.created_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-5 py-3">
                      {req.status === 'pending' && (user?.role === 'admin' || user?.role === 'medecin' || user?.role === 'technicien_labo') && (
                        <div className="flex gap-1">
                          <button
                            onClick={() => handleStatusUpdate(req.id, 'approved')}
                            className="p-1 rounded text-emerald-600 hover:bg-emerald-50 dark:hover:bg-emerald-950"
                            title="Approuver"
                          >
                            <CheckCircle className="h-4 w-4" />
                          </button>
                          <button
                            onClick={() => handleStatusUpdate(req.id, 'cancelled')}
                            className="p-1 rounded text-red-600 hover:bg-red-50 dark:hover:bg-red-950"
                            title="Annuler"
                          >
                            <XCircle className="h-4 w-4" />
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
