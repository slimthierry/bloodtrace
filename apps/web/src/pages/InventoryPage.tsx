import { useState, useEffect } from 'react';
import { Package, Search, AlertTriangle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { clsx } from 'clsx';

interface BloodBag {
  id: number;
  donation_id: number;
  blood_type: string;
  rh_factor: string;
  component: string;
  volume_ml: number;
  collection_date: string;
  expiry_date: string;
  status: string;
  storage_location: string | null;
  storage_temperature: number | null;
}

const STATUS_BADGES: Record<string, string> = {
  available: 'badge-status-available',
  reserved: 'badge-status-reserved',
  crossmatched: 'badge-status-reserved',
  transfused: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  expired: 'badge-status-expired',
  discarded: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400',
  quarantine: 'badge-status-quarantine',
};

const STATUS_LABELS: Record<string, string> = {
  available: 'Disponible',
  reserved: 'Reserve',
  crossmatched: 'Cross-match',
  transfused: 'Transfuse',
  expired: 'Expire',
  discarded: 'Elimine',
  quarantine: 'Quarantaine',
};

const COMPONENT_LABELS: Record<string, string> = {
  whole_blood: 'Sang total',
  packed_rbc: 'CGR',
  plasma: 'Plasma',
  platelets: 'Plaquettes',
  cryoprecipitate: 'Cryoprecipite',
};

export function InventoryPage() {
  const { token } = useAuth();
  const [bags, setBags] = useState<BloodBag[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [alerts, setAlerts] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);

  // Filters
  const [bloodType, setBloodType] = useState('');
  const [component, setComponent] = useState('');
  const [status, setStatus] = useState('');

  const fetchBags = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: '20' });
      if (bloodType) params.set('blood_type', bloodType);
      if (component) params.set('component', component);
      if (status) params.set('status', status);

      const response = await fetch(`/api/v1/inventory?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setBags(data.blood_bags);
        setTotal(data.total);
      }
    } catch {
      // Handle silently
    } finally {
      setLoading(false);
    }
  };

  const fetchAlerts = async () => {
    try {
      const response = await fetch('/api/v1/inventory/stock', {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setAlerts(data.alerts);
      }
    } catch {
      // Handle silently
    }
  };

  useEffect(() => {
    fetchBags();
    fetchAlerts();
  }, [page, bloodType, component, status, token]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)] flex items-center gap-2">
          <Package className="h-6 w-6 text-brand-500" />
          Inventaire des poches de sang
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          {total} poches enregistrees
        </p>
      </div>

      {/* Stock alerts */}
      {alerts.length > 0 && (
        <div className="rounded-lg bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="h-5 w-5 text-amber-600 dark:text-amber-400" />
            <h3 className="text-sm font-semibold text-amber-800 dark:text-amber-300">
              Alertes de stock
            </h3>
          </div>
          <ul className="space-y-1">
            {alerts.map((alert, i) => (
              <li key={i} className="text-sm text-amber-700 dark:text-amber-400">
                {alert}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <select
          value={bloodType}
          onChange={(e) => { setBloodType(e.target.value); setPage(1); }}
          className="input-field w-auto"
        >
          <option value="">Tous les groupes</option>
          <option value="A">A</option>
          <option value="B">B</option>
          <option value="AB">AB</option>
          <option value="O">O</option>
        </select>
        <select
          value={component}
          onChange={(e) => { setComponent(e.target.value); setPage(1); }}
          className="input-field w-auto"
        >
          <option value="">Tous les composants</option>
          <option value="whole_blood">Sang total</option>
          <option value="packed_rbc">CGR (Concentre Globules Rouges)</option>
          <option value="plasma">Plasma</option>
          <option value="platelets">Plaquettes</option>
          <option value="cryoprecipitate">Cryoprecipite</option>
        </select>
        <select
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
          className="input-field w-auto"
        >
          <option value="">Tous les statuts</option>
          <option value="available">Disponible</option>
          <option value="reserved">Reserve</option>
          <option value="crossmatched">Cross-match</option>
          <option value="transfused">Transfuse</option>
          <option value="expired">Expire</option>
          <option value="quarantine">Quarantaine</option>
        </select>
      </div>

      {/* Blood bags table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">Groupe</th>
                <th className="px-5 py-3 font-medium">Composant</th>
                <th className="px-5 py-3 font-medium">Volume</th>
                <th className="px-5 py-3 font-medium">Collecte</th>
                <th className="px-5 py-3 font-medium">Expiration</th>
                <th className="px-5 py-3 font-medium">Statut</th>
                <th className="px-5 py-3 font-medium">Stockage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {loading ? (
                <tr>
                  <td colSpan={8} className="px-5 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-brand-500 border-t-transparent mx-auto" />
                  </td>
                </tr>
              ) : bags.length === 0 ? (
                <tr>
                  <td colSpan={8} className="px-5 py-8 text-center text-[var(--color-text-secondary)]">
                    Aucune poche trouvee
                  </td>
                </tr>
              ) : (
                bags.map((bag) => (
                  <tr key={bag.id} className="hover:bg-[var(--color-bg-secondary)] transition-colors">
                    <td className="px-5 py-3 font-mono text-xs">#{bag.id}</td>
                    <td className="px-5 py-3">
                      <span className="font-bold text-brand-600 dark:text-brand-400">
                        {bag.blood_type}{bag.rh_factor}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {COMPONENT_LABELS[bag.component] || bag.component}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">{bag.volume_ml} mL</td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {new Date(bag.collection_date).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {new Date(bag.expiry_date).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-5 py-3">
                      <span className={clsx('badge', STATUS_BADGES[bag.status])}>
                        {STATUS_LABELS[bag.status] || bag.status}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {bag.storage_location || '-'}
                      {bag.storage_temperature != null && ` (${bag.storage_temperature}C)`}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {total > 20 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-[var(--color-border-primary)]">
            <p className="text-sm text-[var(--color-text-secondary)]">
              Page {page} sur {Math.ceil(total / 20)}
            </p>
            <div className="flex gap-2">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-secondary text-xs">
                Precedent
              </button>
              <button onClick={() => setPage(page + 1)} disabled={page >= Math.ceil(total / 20)} className="btn-secondary text-xs">
                Suivant
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
