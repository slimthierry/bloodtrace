import { useNavigate } from 'react-router-dom';
import { Sun, Moon, LogOut, Bell } from 'lucide-react';
import { useTheme } from '../../context/ThemeContext';
import { useAuth } from '../../context/AuthContext';

function ThemeToggleIcon() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      className="rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)] transition-colors duration-150"
      aria-label={theme === 'dark' ? 'Activer le mode clair' : 'Activer le mode sombre'}
    >
      {theme === 'dark' ? (
        <Sun className="h-5 w-5" />
      ) : (
        <Moon className="h-5 w-5" />
      )}
    </button>
  );
}

export function Header() {
  const { logout, user } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="flex items-center justify-between border-b border-[var(--color-border-primary)] bg-[var(--color-bg-primary)] px-6 py-3">
      <div className="flex items-center gap-4">
        <h2 className="text-sm font-medium text-[var(--color-text-secondary)]">
          Bienvenue, <span className="text-[var(--color-text-primary)]">{user?.name}</span>
        </h2>
      </div>

      <div className="flex items-center gap-2">
        <button
          className="relative rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-[var(--color-bg-tertiary)] hover:text-[var(--color-text-primary)] transition-colors duration-150"
          aria-label="Notifications"
        >
          <Bell className="h-5 w-5" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-brand-500" />
        </button>

        <ThemeToggleIcon />

        <button
          onClick={handleLogout}
          className="rounded-lg p-2 text-[var(--color-text-secondary)] hover:bg-red-50 dark:hover:bg-red-950 hover:text-red-600 dark:hover:text-red-400 transition-colors duration-150"
          aria-label="Se deconnecter"
        >
          <LogOut className="h-5 w-5" />
        </button>
      </div>
    </header>
  );
}
