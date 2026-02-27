import { useState, useEffect } from 'react';
import {
  Droplets,
  AlertTriangle,
  Clock,
  Activity,
  Users,
  Package,
  TrendingUp,
  AlertCircle,
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { clsx } from 'clsx';

interface StockLevel {
  blood_type: string;
  rh_factor: string;
  blood_group: string;
  available: number;
  reserved: number;
  expiring_soon: number;
  total: number;
}

interface DashboardData {
  stock_levels: StockLevel[];
  total_available: number;
  expiring_alerts: Array<{
    blood_bag_id: number;
    blood_group: string;
    component: string;
    expiry_date: string;
    days_remaining: number;
  }>;
  pending_requests: Array<{
    id: number;
    patient_ipp: string;
    patient_name: string;
    blood_group_needed: string;
    component_needed: string;
    units_needed: number;
    urgency: string;
    created_at: string;
  }>;
  recent_transfusions: Array<{
    id: number;
    patient_ipp: string;
    patient_name: string;
    blood_group: string;
    component: string;
    started_at: string;
    reaction_type: string;
  }>;
  stats: {
    total_donors: number;
    total_donations_this_month: number;
    total_transfusions_this_month: number;
    total_blood_bags_available: number;
    total_pending_requests: number;
    reactions_this_month: number;
  };
}

const BLOOD_GROUP_COLORS: Record<string, string> = {
  'A+': 'text-red-600 dark:text-red-400',
  'A-': 'text-red-500 dark:text-red-300',
  'B+': 'text-blue-600 dark:text-blue-400',
  'B-': 'text-blue-500 dark:text-blue-300',
  'AB+': 'text-purple-600 dark:text-purple-400',
  'AB-': 'text-purple-500 dark:text-purple-300',
  'O+': 'text-emerald-600 dark:text-emerald-400',
  'O-': 'text-emerald-500 dark:text-emerald-300',
};

function StockGauge({ level }: { level: StockLevel }) {
  const maxStock = 50;
  const percentage = Math.min((level.available / maxStock) * 100, 100);
  const isLow = level.available < 5;
  const isCritical = level.available === 0;

  return (
    <div className={clsx('card p-4', isCritical && 'ring-2 ring-red-500')}>
      <div className="flex items-center justify-between mb-3">
        <span
          className={clsx(
            'text-2xl font-bold',
            BLOOD_GROUP_COLORS[level.blood_group] || 'text-gray-700 dark:text-gray-300',
          )}
        >
          {level.blood_group}
        </span>
        {isLow && (
          <AlertTriangle
            className={clsx('h-5 w-5', isCritical ? 'text-red-500' : 'text-amber-500')}
          />
        )}
      </div>

      <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3 mb-2">
        <div
          className={clsx(
            'h-3 rounded-full transition-all duration-500',
            isCritical
              ? 'bg-red-600'
              : isLow
                ? 'bg-amber-500'
                : 'bg-brand-500',
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex justify-between text-xs text-[var(--color-text-secondary)]">
        <span>{level.available} disponibles</span>
        <span>{level.reserved} reserves</span>
      </div>

      {level.expiring_soon > 0 && (
        <p className="mt-1 text-xs text-amber-600 dark:text-amber-400">
          {level.expiring_soon} expirant bientot
        </p>
      )}
    </div>
  );
}

export function DashboardPage() {
  const { token } = useAuth();
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const response = await fetch('/api/v1/dashboard', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          setData(await response.json());
        }
      } catch {
        // Handle error silently for demo
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [token]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-brand-500 border-t-transparent" />
      </div>
    );
  }

  const stats = data?.stats;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">
          Tableau de bord
        </h1>
        <p className="text-sm text-[var(--color-text-secondary)] mt-1">
          Vue d'ensemble de la banque de sang
        </p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {[
          { label: 'Donneurs', value: stats?.total_donors ?? 0, icon: Users, color: 'text-blue-600 dark:text-blue-400' },
          { label: 'Dons (mois)', value: stats?.total_donations_this_month ?? 0, icon: Droplets, color: 'text-brand-600 dark:text-brand-400' },
          { label: 'Transfusions (mois)', value: stats?.total_transfusions_this_month ?? 0, icon: Activity, color: 'text-emerald-600 dark:text-emerald-400' },
          { label: 'Poches disponibles', value: stats?.total_blood_bags_available ?? 0, icon: Package, color: 'text-purple-600 dark:text-purple-400' },
          { label: 'Demandes en attente', value: stats?.total_pending_requests ?? 0, icon: Clock, color: 'text-amber-600 dark:text-amber-400' },
          { label: 'Reactions (mois)', value: stats?.reactions_this_month ?? 0, icon: AlertCircle, color: 'text-red-600 dark:text-red-400' },
        ].map((stat) => (
          <div key={stat.label} className="card p-4">
            <div className="flex items-center gap-2 mb-2">
              <stat.icon className={clsx('h-4 w-4', stat.color)} />
              <span className="text-xs text-[var(--color-text-secondary)]">{stat.label}</span>
            </div>
            <p className="text-2xl font-bold text-[var(--color-text-primary)]">
              {stat.value}
            </p>
          </div>
        ))}
      </div>

      {/* Stock gauges - 8 blood groups */}
      <div>
        <h2 className="text-lg font-semibold text-[var(--color-text-primary)] mb-3">
          Niveaux de stock par groupe sanguin
        </h2>
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
          {(data?.stock_levels ?? []).map((level) => (
            <StockGauge key={level.blood_group} level={level} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Expiring alerts */}
        <div className="card">
          <div className="px-5 py-4 border-b border-[var(--color-border-primary)]">
            <h3 className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-amber-500" />
              Poches expirant bientot
            </h3>
          </div>
          <div className="divide-y divide-[var(--color-border-primary)]">
            {(data?.expiring_alerts ?? []).length === 0 ? (
              <p className="px-5 py-4 text-sm text-[var(--color-text-secondary)]">
                Aucune alerte d'expiration
              </p>
            ) : (
              data?.expiring_alerts.map((alert) => (
                <div key={alert.blood_bag_id} className="px-5 py-3 flex items-center justify-between">
                  <div>
                    <span className="text-sm font-medium text-[var(--color-text-primary)]">
                      Poche #{alert.blood_bag_id}
                    </span>
                    <span className="ml-2 badge badge-blood-a">
                      {alert.blood_group}
                    </span>
                    <p className="text-xs text-[var(--color-text-secondary)]">
                      {alert.component}
                    </p>
                  </div>
                  <span className={clsx(
                    'text-xs font-medium',
                    alert.days_remaining <= 2 ? 'text-red-600 dark:text-red-400' : 'text-amber-600 dark:text-amber-400',
                  )}>
                    {alert.days_remaining}j restants
                  </span>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Pending requests */}
        <div className="card">
          <div className="px-5 py-4 border-b border-[var(--color-border-primary)]">
            <h3 className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
              <Clock className="h-4 w-4 text-brand-500" />
              Demandes en attente
            </h3>
          </div>
          <div className="divide-y divide-[var(--color-border-primary)]">
            {(data?.pending_requests ?? []).length === 0 ? (
              <p className="px-5 py-4 text-sm text-[var(--color-text-secondary)]">
                Aucune demande en attente
              </p>
            ) : (
              data?.pending_requests.map((req) => (
                <div key={req.id} className="px-5 py-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-[var(--color-text-primary)]">
                      {req.patient_name}
                    </span>
                    <span className={`badge badge-urgency-${req.urgency}`}>
                      {req.urgency}
                    </span>
                  </div>
                  <p className="text-xs text-[var(--color-text-secondary)] mt-0.5">
                    IPP: {req.patient_ipp} | {req.blood_group_needed} {req.component_needed} x{req.units_needed}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Recent transfusions */}
      <div className="card">
        <div className="px-5 py-4 border-b border-[var(--color-border-primary)]">
          <h3 className="text-sm font-semibold text-[var(--color-text-primary)] flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-emerald-500" />
            Transfusions recentes
          </h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs text-[var(--color-text-secondary)] border-b border-[var(--color-border-primary)]">
                <th className="px-5 py-3 font-medium">Patient</th>
                <th className="px-5 py-3 font-medium">IPP</th>
                <th className="px-5 py-3 font-medium">Groupe</th>
                <th className="px-5 py-3 font-medium">Composant</th>
                <th className="px-5 py-3 font-medium">Date</th>
                <th className="px-5 py-3 font-medium">Reaction</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--color-border-primary)]">
              {(data?.recent_transfusions ?? []).length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-5 py-4 text-center text-[var(--color-text-secondary)]">
                    Aucune transfusion recente
                  </td>
                </tr>
              ) : (
                data?.recent_transfusions.map((t) => (
                  <tr key={t.id}>
                    <td className="px-5 py-3 font-medium text-[var(--color-text-primary)]">{t.patient_name}</td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">{t.patient_ipp}</td>
                    <td className="px-5 py-3">
                      <span className={clsx('font-semibold', BLOOD_GROUP_COLORS[t.blood_group])}>
                        {t.blood_group}
                      </span>
                    </td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">{t.component}</td>
                    <td className="px-5 py-3 text-[var(--color-text-secondary)]">
                      {new Date(t.started_at).toLocaleDateString('fr-FR')}
                    </td>
                    <td className="px-5 py-3">
                      <span className={clsx(
                        'badge',
                        t.reaction_type === 'none'
                          ? 'badge-status-available'
                          : t.reaction_type === 'severe'
                            ? 'badge-status-expired'
                            : 'badge-status-reserved',
                      )}>
                        {t.reaction_type === 'none' ? 'Aucune' : t.reaction_type}
                      </span>
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
