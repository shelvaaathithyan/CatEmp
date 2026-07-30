import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import ProtectedRoute from './components/common/ProtectedRoute';
import PlaceholderPage from './components/common/PlaceholderPage';

import Login from './pages/auth/Login';
import DealerLayout from './layouts/DealerLayout';
import CustomerLayout from './layouts/CustomerLayout';
import FleetManagerLayout from './layouts/FleetManagerLayout';

const PublicOnlyRoute = ({ children }) => {
  const { user, token, isLoading } = useAuth();
  if (isLoading) return null;
  if (token && user) {
    if (user.role === 'Dealer') return <Navigate to="/dealer/dashboard" replace />;
    if (user.role === 'Customer') return <Navigate to="/customer/dashboard" replace />;
    if (user.role === 'Fleet Manager') return <Navigate to="/fleet/dashboard" replace />;
    return <Navigate to="/" replace />;
  }
  return children;
};

const RootRedirect = () => {
  const { user, token, isLoading } = useAuth();
  if (isLoading) return null;
  if (!token || !user) return <Navigate to="/login" replace />;
  if (user.role === 'Dealer') return <Navigate to="/dealer/dashboard" replace />;
  if (user.role === 'Customer') return <Navigate to="/customer/dashboard" replace />;
  if (user.role === 'Fleet Manager') return <Navigate to="/fleet/dashboard" replace />;
  return <Navigate to="/login" replace />;
};

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootRedirect />} />
          
          <Route path="/login" element={
            <PublicOnlyRoute>
              <Login />
            </PublicOnlyRoute>
          } />

          {/* Dealer Routes */}
          <Route path="/dealer" element={<ProtectedRoute allowedRoles={['Dealer', 'CatAdmin']}><DealerLayout /></ProtectedRoute>}>
            <Route path="dashboard" element={<PlaceholderPage title="Dashboard" description="Overview of dealer operations" />} />
            <Route path="machines" element={<PlaceholderPage title="Machines" description="Manage machine inventory" />} />
            <Route path="rentals" element={<PlaceholderPage title="Rentals" description="Track all active and past rentals" />} />
            <Route path="maintenance" element={<PlaceholderPage title="Maintenance" description="Maintenance schedules and logs" />} />
            <Route path="predictions" element={<PlaceholderPage title="Predictions" description="AI-driven utilization predictions" />} />
            <Route path="notifications" element={<PlaceholderPage title="Notifications" description="Alerts and system messages" />} />
          </Route>

          {/* Customer Routes */}
          <Route path="/customer" element={<ProtectedRoute allowedRoles={['Customer']}><CustomerLayout /></ProtectedRoute>}>
            <Route path="dashboard" element={<PlaceholderPage title="Dashboard" description="Customer overview" />} />
            <Route path="sites" element={<PlaceholderPage title="Sites" description="Manage your work sites" />} />
            <Route path="rentals" element={<PlaceholderPage title="Rentals" description="Your rental agreements" />} />
            <Route path="usage" element={<PlaceholderPage title="Equipment Usage" description="Track how machines are being used" />} />
            <Route path="predictions" element={<PlaceholderPage title="Predictions" description="Demand predictions" />} />
            <Route path="notifications" element={<PlaceholderPage title="Notifications" description="Alerts and updates" />} />
          </Route>

          {/* Fleet Manager Routes */}
          <Route path="/fleet" element={<ProtectedRoute allowedRoles={['Fleet Manager']}><FleetManagerLayout /></ProtectedRoute>}>
            <Route path="dashboard" element={<PlaceholderPage title="Dashboard" description="Fleet management overview" />} />
            <Route path="site" element={<PlaceholderPage title="My Site" description="Site details and operations" />} />
            <Route path="usage" element={<PlaceholderPage title="Equipment Usage" description="Machine operation logs" />} />
            <Route path="transfers" element={<PlaceholderPage title="Transfers" description="Site-to-site machine transfers" />} />
            <Route path="checkin" element={<PlaceholderPage title="Check In / Out" description="Manage physical machine movement" />} />
            <Route path="notifications" element={<PlaceholderPage title="Notifications" description="Important fleet alerts" />} />
          </Route>

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
