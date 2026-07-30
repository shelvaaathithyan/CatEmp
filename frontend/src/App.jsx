import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { WebSocketProvider } from './contexts/WebSocketContext';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import ProtectedRoute from './components/common/ProtectedRoute';
import PlaceholderPage from './components/common/PlaceholderPage';

import Login from './pages/auth/Login';
import DealerLayout from './layouts/DealerLayout';
import CustomerLayout from './layouts/CustomerLayout';
import FleetManagerLayout from './layouts/FleetManagerLayout';

import DealerDashboard from './pages/dealer/DealerDashboard';
import CustomerDashboard from './pages/customer/CustomerDashboard';
import FleetDashboard from './pages/fleet/FleetDashboard';
import FleetSites from './pages/fleet/FleetSites';
import FleetUsage from './pages/fleet/FleetUsage';
import FleetTransfers from './pages/fleet/FleetTransfers';
import FleetCheckin from './pages/fleet/FleetCheckin';
import FleetNotifications from './pages/fleet/FleetNotifications';

import DealerMachines from './pages/dealer/DealerMachines';
import DealerRentals from './pages/dealer/DealerRentals';
import DealerMaintenance from './pages/dealer/DealerMaintenance';
import DealerNotifications from './pages/dealer/DealerNotifications';

import CustomerRentals from './pages/customer/CustomerRentals';
import CustomerOperators from './pages/customer/CustomerOperators';
import CustomerSites from './pages/customer/CustomerSites';
import CustomerUsage from './pages/customer/CustomerUsage';
import CustomerNotifications from './pages/customer/CustomerNotifications';

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
      <WebSocketProvider>
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
              <Route path="dashboard" element={<DealerDashboard />} />
              <Route path="machines" element={<DealerMachines />} />
              <Route path="rentals" element={<DealerRentals />} />
              <Route path="maintenance" element={<DealerMaintenance />} />
              <Route path="predictions" element={<PlaceholderPage title="Predictions" description="AI-driven utilization predictions" />} />
              <Route path="notifications" element={<DealerNotifications />} />
            </Route>

            {/* Customer Routes */}
            <Route path="/customer" element={<ProtectedRoute allowedRoles={['Customer']}><CustomerLayout /></ProtectedRoute>}>
              <Route path="dashboard" element={<CustomerDashboard />} />
              <Route path="sites" element={<CustomerSites />} />
              <Route path="rentals" element={<CustomerRentals />} />
              <Route path="operators" element={<CustomerOperators />} />
              <Route path="usage" element={<CustomerUsage />} />
              <Route path="predictions" element={<PlaceholderPage title="Predictions" description="Demand predictions" />} />
              <Route path="notifications" element={<CustomerNotifications />} />
            </Route>

            {/* Fleet Manager Routes */}
            <Route path="/fleet" element={<ProtectedRoute allowedRoles={['Fleet Manager']}><FleetManagerLayout /></ProtectedRoute>}>
              <Route path="dashboard" element={<FleetDashboard />} />
              <Route path="site" element={<FleetSites />} />
              <Route path="usage" element={<FleetUsage />} />
              <Route path="transfers" element={<FleetTransfers />} />
              <Route path="checkin" element={<FleetCheckin />} />
              <Route path="notifications" element={<FleetNotifications />} />
            </Route>

          </Routes>
          <ToastContainer position="bottom-right" theme="dark" />
        </BrowserRouter>
      </WebSocketProvider>
    </AuthProvider>
  );
}

export default App;
