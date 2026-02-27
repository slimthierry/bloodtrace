import { useState, useEffect } from 'react';
import { Activity, Link as LinkIcon, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { clsx } from 'clsx';

interface Transfusion {
  id: number;
  request_id: number;
  blood_bag_id: number;
  patient_ipp: string;
  administering_nurse_id: number;
  started_at: string;
  completed_at: string | null;
  reaction_type: string;
  reaction_details: string | null;
  vital_signs_pre: Record<string, unknown> | null;
  vital_signs_post: Record<string, unknown> | null;
}

interface TraceabilityChain {
  donor_ipp: string;
  donor_name: string;
  donor_blood_group: string;
  donation_id: number;
  donation_date: string;
  blood_bag_id: number;
  blood_bag_component: string;
  transfusion_id: number;
  patient_ipp: string;
  patient_name: string;
  transfusion_date: string;
  reaction_type: string;
}

const REACTION_BADGES: Record<string, string> = {
  none: 'badge-status-available',
  mild: 'badge-urgency-urgent',
  moderate: 'badge-urgency-emergency',
  severe: 'badge-urgency-massive',
};

const REACTION_LABELS: Record<string, string> = {
  none: 'Aucune',
  mild: 'Legere',
  moderate: 'Moderee',
  severe: 'Severe',
};

export function TransfusionsPage() {
  const { token } = useAuth();
  const [transfusions, setTransfusions] = useState<Transfusion[]>([]);
  const [selectedTrace, setSelectedTrace] = useState<TraceabilityChain | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch recent transfusions via dashboard
        const response = await fetch('/api/v1/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          // Map dashboard transfusions to the component format
          setTransfusions(
            data.recent_transfusions.map((t: { id: number; patient_ipp: string; started_at: string; reaction_type: string }) => ({
              id: t.id,
              patient_ipp: t.patient_ipp,
              started_at: t.started_at,
              reaction_type: t.reaction_type,
              request_id: 0,
              blood_bag_id: 0,
              administering_nurse_id: 0,
              completed_at: null,
              reaction_details: null,
              vital_signs_pre: null,
              vital_signs_post: null,
            })),
          );
        }
      } catch {
        // Handle silently
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [token]);

  const loadTrace = async (transfusionId: number) => {
    try {
      const response = await fetch(`/api/v1/transfusions/${transfusionId}/trace`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setSelectedTrace(data);
      }
    } catch {
      // Handle silently
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)] flex items-center gap-2">
          <Activity className="h-6 w-6 text-brand-500" />
          Transfusions
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          Suivi des transfusions et tracabilite complete
        </p>
      </div>

      {/* Traceability chain display */}
      {selectedTrace && (
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <LinkIcon className="h-5 w-5 text-brand-500" />
              Chaine de tracabilite
            </h2>
            <button
              onClick={() => setSelectedTrace(null)}
              className="text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)]"
            >
              Fermer
            </button>
          </div>

          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {/* Donor */}
            <div className="flex-shrink-0 card p-4 min-w-[180px] border-l-4 border-l-blue-500">
              <p className="text-xs text-[var(--color-text-secondary)]">Donneur</p>
              <p className="font-semibold text-[var(--color-text-primary)]">{selectedTrace.donor_name}</p>
              <p className="text-xs text-[var(--color-text-secondary)]">IPP: {selectedTrace.donor_ipp}</p>
              <p className="text-sm font-bold text-brand-600 dark:text-brand-400 mt-1">
                {selectedTrace.donor_blood_group}
              </p>
            </div>

            <div className="text-2xl text-[var(--color-text-secondary)]">&rarr;</div>

            {/* Donation */}
            <div className="flex-shrink-0 card p-4 min-w-[180px] border-l-4 border-l-emerald-500">
              <p className="text-xs text-[var(--color-text-secondary)]">Don</p>
              <p className="font-semibold text-[var(--color-text-primary)]">Don #{selectedTrace.donation_id}</p>
              <p className="text-xs text-[var(--color-text-secondary)]">
                {new Date(selectedTrace.donation_date).toLocaleDateString('fr-FR')}
              </p>
            </div>

            <div className="text-2xl text-[var(--color-text-secondary)]">&rarr;</div>

            {/* Blood bag */}
            <div className="flex-shrink-0 card p-4 min-w-[180px] border-l-4 border-l-purple-500">
              <p className="text-xs text-[var(--color-text-secondary)]">Poche</p>
              <p className="font-semibold text-[var(--color-text-primary)]">Poche #{selectedTrace.blood_bag_id}</p>
              <p className="text-xs text-[var(--color-text-secondary)]">{selectedTrace.blood_bag_component}</p>
            </div>

            <div className="text-2xl text-[var(--color-text-secondary)]">&rarr;</div>

            {/* Patient */}
            <div className="flex-shrink-0 card p-4 min-w-[180px] border-l-4 border-l-brand-500">
              <p className="text-xs text-[var(--color-text-secondary)]">Patient</p>
              <p className="font-semibold text-[var(--color-text-primary)]">{selectedTrace.patient_name}</p>
              <p className="text-xs text-[var(--color-text-secondary)]">IPP: {selectedTrace.patient_ipp}</p>
              <div className="mt-1">
                <span className={clsx('badge', REACTION_BADGES[selectedTrace.reaction_type])}>
                  Reaction: {REACTION_LABELS[selectedTrace.reaction_type]}
                </span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Transfusions table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-primary)] bg-[var(--color-bg-secondary)]">
                <th className="px-5 py-3 font-medium">ID</th>
                <th className="px-5 py-3 font-medium">Patient IPP</th>
                <th className="px-5 py-3 font-medium">Debut</th>
                <th className="px-5 py-3 font-medium">Fin</th>
                <th className="px-5 py-3 font-medium">Reaction</th>
                <th className="px-5 py-3 font-medium">Tracabilite</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {loading ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-brand-500 border-t-transparent mx-auto" />
                  </td>
                </tr>
              ) : transfusions.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-8 text-center text-[var(--color-text-secondary)]">
                    Aucune transfusion enregistree
                  </td>
                </tr>
              ) : (
                transfusions.map((t) => (
                  <tr key={t.id} className="hover:bg-[var(--color-bg-secondary)] transition-colors">
                    <td className="px-5 py-3 font-mono text-xs">#{t.id}</td>
                    <td className="px-5 py-3 font-medium text-[var(--color-text-primary)]">{t.patient_ipp}</td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {new Date(t.started_at).toLocaleString('fr-FR')}
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {t.completed_at ? new Date(t.completed_at).toLocaleString('fr-FR') : 'En cours'}
                    </td>
                    <td className="px-5 py-3">
                      <span className={clsx('badge', REACTION_BADGES[t.reaction_type])}>
                        {REACTION_LABELS[t.reaction_type] || t.reaction_type}
                      </span>
                    </td>
                    <td className="px-5 py-3">
                      <button
                        onClick={() => loadTrace(t.id)}
                        className="inline-flex items-center gap-1 text-xs text-brand-600 dark:text-brand-400 hover:underline"
                      >
                        <LinkIcon className="h-3 w-3" />
                        Voir la chaine
                      </button>
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
