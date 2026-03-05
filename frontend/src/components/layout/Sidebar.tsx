import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  Users,
  Package,
  FileText,
  Activity,
  Shield,
  Droplets,
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { clsx } from 'clsx';

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Donneurs', href: '/donors', icon: Users },
  { name: 'Inventaire', href: '/inventory', icon: Package },
  { name: 'Demandes', href: '/requests', icon: FileText },
  { name: 'Transfusions', href: '/transfusions', icon: Activity },
  { name: 'Audit', href: '/audit', icon: Shield, adminOnly: true },
];

export function Sidebar() {
  const { user } = useAuth();

  return (
    <aside className="hidden lg:flex lg:flex-col lg:w-64 border-r border-[var(--color-border-primary)] bg-[var(--color-bg-primary)]">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-5 border-b border-[var(--color-border-primary)]">
        <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-500">
          <Droplets className="w-5 h-5 text-white" />
        </div>
        <div>
          <h1 className="text-lg font-bold text-[var(--color-text-primary)]">
            BloodTrace
          </h1>
          <p className="text-xs text-[var(--color-text-secondary)]">
            Module SIH
          </p>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navigation.map((item) => {
          if (item.adminOnly && user?.role !== 'admin') return null;

          return (
            <NavLink
              key={item.href}
              to={item.href}
              className={({ isActive }) =>
                clsx(
                  'flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors duration-150',
                  isActive
                    ? 'bg-brand-50 dark:bg-brand-950 text-brand-600 dark:text-brand-400'
                    : 'text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)]',
                )
              }
            >
              <item.icon className="h-5 w-5 flex-shrink-0" />
              {item.name}
            </NavLink>
          );
        })}
      </nav>

      {/* User info */}
      <div className="border-t border-[var(--color-border-primary)] px-4 py-3">
        <div className="flex items-center gap-3">
          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-brand-100 dark:bg-brand-900">
            <span className="text-sm font-medium text-brand-700 dark:text-brand-300">
              {user?.name?.charAt(0)?.toUpperCase() || '?'}
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-[var(--color-text-primary)]">
              {user?.name}
            </p>
            <p className="truncate text-xs text-[var(--color-text-secondary)]">
              {user?.role}
            </p>
          </div>
        </div>
      </div>
    </aside>
  );
}
