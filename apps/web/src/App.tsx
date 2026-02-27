import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import { AuthProvider } from './context/AuthContext';
import { AppLayout } from './components/layout/AppLayout';
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { DonorsPage } from './pages/DonorsPage';
import { InventoryPage } from './pages/InventoryPage';
import { RequestsPage } from './pages/RequestsPage';
import { TransfusionsPage } from './pages/TransfusionsPage';
import { AuditPage } from './pages/AuditPage';

function App() {
  return (
    <ThemeProvider storageKey="bloodtrace-theme">
      <AuthProvider>
        <BrowserRouter>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/" element={<AppLayout />}>
              <Route index element={<Navigate to="/dashboard" replace />} />
              <Route path="dashboard" element={<DashboardPage />} />
              <Route path="donors" element={<DonorsPage />} />
              <Route path="inventory" element={<InventoryPage />} />
              <Route path="requests" element={<RequestsPage />} />
              <Route path="transfusions" element={<TransfusionsPage />} />
              <Route path="audit" element={<AuditPage />} />
            </Route>
          </Routes>
        </BrowserRouter>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
