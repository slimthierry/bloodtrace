import { useState, useEffect } from 'react';
import { Shield, Search, Filter } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { clsx } from 'clsx';

interface AuditLog {
  id: number;
  user_id: number | null;
  user_name: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  details: Record<string, unknown>;
  ip_address: string | null;
  timestamp: string;
}

const ACTION_BADGES: Record<string, string> = {
  create: 'badge-status-available',
  read: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
  update: 'badge-status-reserved',
  delete: 'badge-status-expired',
};

export function AuditPage() {
  const { token } = useAuth();
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);

  // Filters
  const [actionFilter, setActionFilter] = useState('');
  const [entityFilter, setEntityFilter] = useState('');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');

  const fetchLogs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({ page: String(page), page_size: '50' });
      if (actionFilter) params.set('action', actionFilter);
      if (entityFilter) params.set('entity_type', entityFilter);
      if (dateFrom) params.set('date_from', new Date(dateFrom).toISOString());
      if (dateTo) params.set('date_to', new Date(dateTo).toISOString());

      const response = await fetch(`/api/v1/audit?${params}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setLogs(data.logs);
        setTotal(data.total);
      }
    } catch {
      // Handle silently
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [page, actionFilter, entityFilter, dateFrom, dateTo, token]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)] flex items-center gap-2">
          <Shield className="h-6 w-6 text-brand-500" />
          Journal d'audit
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          Tracabilite complete des acces et modifications - {total} entrees
        </p>
      </div>

      {/* Filters */}
      <div className="card p-4">
        <div className="flex items-center gap-2 mb-3">
          <Filter className="h-4 w-4 text-[var(--color-text-secondary)]" />
          <span className="text-sm font-medium text-[var(--color-text-primary)]">Filtres</span>
        </div>
        <div className="flex flex-wrap gap-3">
          <select
            value={actionFilter}
            onChange={(e) => { setActionFilter(e.target.value); setPage(1); }}
            className="input-field w-auto"
          >
            <option value="">Toutes les actions</option>
            <option value="create">Creation</option>
            <option value="read">Lecture</option>
            <option value="update">Modification</option>
            <option value="delete">Suppression</option>
          </select>
          <select
            value={entityFilter}
            onChange={(e) => { setEntityFilter(e.target.value); setPage(1); }}
            className="input-field w-auto"
          >
            <option value="">Toutes les entites</option>
            <option value="donor">Donneurs</option>
            <option value="donation">Dons</option>
            <option value="blood_bag">Poches de sang</option>
            <option value="transfusion_request">Demandes</option>
            <option value="transfusion">Transfusions</option>
            <option value="auth">Authentification</option>
          </select>
          <div>
            <input
              type="date"
              value={dateFrom}
              onChange={(e) => { setDateFrom(e.target.value); setPage(1); }}
              className="input-field"
              placeholder="Date debut"
            />
          </div>
          <div>
            <input
              type="date"
              value={dateTo}
              onChange={(e) => { setDateTo(e.target.value); setPage(1); }}
              className="input-field"
              placeholder="Date fin"
            />
          </div>
        </div>
      </div>

      {/* Audit logs table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-5 py-3 font-medium">Horodatage</th>
                <th className="px-5 py-3 font-medium">Utilisateur</th>
                <th className="px-5 py-3 font-medium">Action</th>
                <th className="px-5 py-3 font-medium">Entite</th>
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">IP</th>
                <th className="px-5 py-3 font-medium">Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {loading ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-brand-500 border-t-transparent mx-auto" />
                  </td>
                </tr>
              ) : logs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-8 text-center text-[var(--color-text-secondary)]">
                    Aucune entree d'audit trouvee
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.id} className="hover:bg-[var(--color-bg-secondary)] transition-colors">
                    <td className="px-5 py-3 text-xs text-[var(--color-text-secondary)] whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleString('fr-FR')}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-primary)]">
                      {log.user_name || 'Systeme'}
                    </td>
                    <td className="px-5 py-3">
                      <span className={clsx('badge', ACTION_BADGES[log.action] || 'badge-urgency-routine')}>
                        {log.action}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {log.entity_type}
                    </td>
                    <td className="px-5 py-3 font-mono text-xs text-[var(--color-text-secondary)]">
                      {log.entity_id || '-'}
                    </td>
                    <td className="px-5 py-3 font-mono text-xs text-[var(--color-text-secondary)]">
                      {log.ip_address || '-'}
                    </td>
                    <td className="px-5 py-3">
                      <pre className="text-xs text-[var(--color-text-secondary)] max-w-xs truncate">
                        {JSON.stringify(log.details)}
                      </pre>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {total > 50 && (
          <div className="flex items-center justify-between px-5 py-3 border-t border-[var(--color-border-primary)]">
            <p className="text-sm text-[var(--color-text-secondary)]">
              Page {page} sur {Math.ceil(total / 50)}
            </p>
            <div className="flex gap-2">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1} className="btn-secondary text-xs">
                Precedent
              </button>
              <button onClick={() => setPage(page + 1)} disabled={page >= Math.ceil(total / 50)} className="btn-secondary text-xs">
                Suivant
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
