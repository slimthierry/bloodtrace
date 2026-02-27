import { useState, useEffect, type FormEvent } from 'react';
import { Users, Plus, Search, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { clsx } from 'clsx';

interface Donor {
  id: number;
  ipp: string;
  first_name: string;
  last_name: string;
  date_of_birth: string;
  blood_type: string;
  rh_factor: string;
  eligibility_status: string;
  donation_count: number;
  last_donation_date: string | null;
  phone: string | null;
  email: string | null;
}

const ELIGIBILITY_BADGES: Record<string, string> = {
  eligible: 'badge-status-available',
  temporary_deferral: 'badge-status-reserved',
  permanent_deferral: 'badge-status-expired',
};

const ELIGIBILITY_LABELS: Record<string, string> = {
  eligible: 'Eligible',
  temporary_deferral: 'Ajournement temp.',
  permanent_deferral: 'Ajournement perm.',
};

export function DonorsPage() {
  const { token } = useAuth();
  const [donors, setDonors] = useState<Donor[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [bloodTypeFilter, setBloodTypeFilter] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchDonors = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: '20' });
      if (search) params.set('search', search);
      if (bloodTypeFilter) params.set('blood_type', bloodTypeFilter);

      const response = await fetch(`/api/v1/donors?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setDonors(data.donors);
        setTotal(data.total);
      }
    } catch {
      // Handle silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDonors();
  }, [page, search, bloodTypeFilter, token]);

  const handleRegister = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const formData = new FormData(form);

    try {
      const response = await fetch('/api/v1/donors', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ipp: formData.get('ipp'),
          first_name: formData.get('first_name'),
          last_name: formData.get('last_name'),
          date_of_birth: formData.get('date_of_birth'),
          blood_type: formData.get('blood_type'),
          rh_factor: formData.get('rh_factor'),
          phone: formData.get('phone') || null,
          email: formData.get('email') || null,
        }),
      });

      if (response.ok) {
        setShowForm(false);
        fetchDonors();
      }
    } catch {
      // Handle silently
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)] flex items-center gap-2">
            <Users className="h-6 w-6 text-brand-500" />
            Registre des donneurs
          </h1>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            {total} donneurs enregistres
          </p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          <Plus className="h-4 w-4 mr-2" />
          Nouveau donneur
        </button>
      </div>

      {/* Registration form */}
      {showForm && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-[var(--color-text-primary)]">
              Enregistrer un nouveau donneur
            </h2>
            <button onClick={() => setShowForm(false)} className="text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]">
              <X className="h-5 w-5" />
            </button>
          </div>
          <form onSubmit={handleRegister} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">IPP</label>
              <input name="ipp" className="input-field" placeholder="Identifiant Permanent du Patient" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Prenom</label>
              <input name="first_name" className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Nom</label>
              <input name="last_name" className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Date de naissance</label>
              <input name="date_of_birth" type="date" className="input-field" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Groupe sanguin</label>
              <select name="blood_type" className="input-field" required>
                <option value="">Selectionner</option>
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="AB">AB</option>
                <option value="O">O</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Rhesus</label>
              <select name="rh_factor" className="input-field" required>
                <option value="">Selectionner</option>
                <option value="+">Positif (+)</option>
                <option value="-">Negatif (-)</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Telephone</label>
              <input name="phone" type="tel" className="input-field" />
            </div>
            <div>
              <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">Email</label>
              <input name="email" type="email" className="input-field" />
            </div>
            <div className="flex items-end">
              <button type="submit" className="btn-primary w-full">
                Enregistrer
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-[var(--color-text-secondary)]" />
          <input
            type="text"
            placeholder="Rechercher par nom ou IPP..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-field pl-9"
          />
        </div>
        <select
          value={bloodTypeFilter}
          onChange={(e) => setBloodTypeFilter(e.target.value)}
          className="input-field w-auto"
        >
          <option value="">Tous les groupes</option>
          <option value="A">Groupe A</option>
          <option value="B">Groupe B</option>
          <option value="AB">Groupe AB</option>
          <option value="O">Groupe O</option>
        </select>
      </div>

      {/* Donors table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-5 py-3 font-medium">IPP</th>
                <th className="px-5 py-3 font-medium">Nom</th>
                <th className="px-5 py-3 font-medium">Date de naissance</th>
                <th className="px-5 py-3 font-medium">Groupe</th>
                <th className="px-5 py-3 font-medium">Eligibilite</th>
                <th className="px-5 py-3 font-medium">Dons</th>
                <th className="px-5 py-3 font-medium">Dernier don</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-brand-500 border-t-transparent mx-auto" />
                  </td>
                </tr>
              ) : donors.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center text-[var(--color-text-secondary)]">
                    Aucun donneur trouve
                  </td>
                </tr>
              ) : (
                donors.map((donor) => (
                  <tr key={donor.id} className="hover:bg-[var(--color-bg-secondary)] transition-colors">
                    <td className="px-5 py-3 font-mono text-xs">{donor.ipp}</td>
                    <td className="px-5 py-3 font-medium text-[var(--color-text-primary)]">
                      {donor.first_name} {donor.last_name}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {new Date(donor.date_of_birth).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-5 py-3">
                      <span className="font-bold text-brand-600 dark:text-brand-400">
                        {donor.blood_type}{donor.rh_factor}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <span className={clsx('badge', ELIGIBILITY_BADGES[donor.eligibility_status])}>
                        {ELIGIBILITY_LABELS[donor.eligibility_status] || donor.eligibility_status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">{donor.donation_count}</td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {donor.last_donation_date
                        ? new Date(donor.last_donation_date).toLocaleDateString('fr-FR')
                        : '-'}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {total > 20 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-[var(--color-border-primary)]">
            <p className="text-sm text-[var(--color-text-secondary)]">
              Page {page} sur {Math.ceil(total / 20)}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
                className="btn-secondary text-xs"
              >
                Precedent
              </button>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page >= Math.ceil(total / 20)}
                className="btn-secondary text-xs"
              >
                Suivant
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
