/**
 * @bloodtrace/theme - Theme configuration for BloodTrace
 *
 * Brand color: Red #DC2626
 * Storage key: 'bloodtrace-theme'
 */

export const STORAGE_KEY = 'bloodtrace-theme';

export const brand = {
  50: '#FEF2F2',
  100: '#FEE2E2',
  200: '#FECACA',
  300: '#FCA5A5',
  400: '#F87171',
  500: '#DC2626',
  600: '#B91C1C',
  700: '#991B1B',
  800: '#7F1D1D',
  900: '#671D1D',
  950: '#450A0A',
} as const;

export const semantic = {
  light: {
    bgPrimary: '#ffffff',
    bgSecondary: '#f9fafb',
    bgTertiary: '#f3f4f6',
    bgAccent: brand[50],
    textPrimary: '#111827',
    textSecondary: '#6b7280',
    textAccent: brand[600],
    borderPrimary: '#e5e7eb',
    borderAccent: brand[200],
  },
  dark: {
    bgPrimary: '#0f172a',
    bgSecondary: '#1e293b',
    bgTertiary: '#334155',
    bgAccent: brand[950],
    textPrimary: '#f1f5f9',
    textSecondary: '#94a3b8',
    textAccent: brand[400],
    borderPrimary: '#334155',
    borderAccent: brand[800],
  },
} as const;

export const bloodTypeColors = {
  A: { text: '#DC2626', bg: '#FEF2F2' },
  B: { text: '#2563EB', bg: '#EFF6FF' },
  AB: { text: '#7C3AED', bg: '#F5F3FF' },
  O: { text: '#059669', bg: '#ECFDF5' },
} as const;

export const statusColors = {
  available: { text: '#059669', bg: '#ECFDF5' },
  reserved: { text: '#D97706', bg: '#FFFBEB' },
  expired: { text: '#DC2626', bg: '#FEF2F2' },
  quarantine: { text: '#7C3AED', bg: '#F5F3FF' },
} as const;

export const urgencyColors = {
  routine: { text: '#6B7280', bg: '#F9FAFB' },
  urgent: { text: '#D97706', bg: '#FFFBEB' },
  emergency: { text: '#DC2626', bg: '#FEF2F2' },
  massive: { text: '#7F1D1D', bg: '#FEE2E2' },
} as const;
