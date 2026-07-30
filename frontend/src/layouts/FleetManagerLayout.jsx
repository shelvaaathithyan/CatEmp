import DashboardLayout from './DashboardLayout';

const FleetManagerLayout = () => {
  const links = [
    { path: '/fleet/dashboard', label: 'Dashboard' },
    { path: '/fleet/site', label: 'Sites' },
    { path: '/fleet/operators', label: 'Operators' },
    { path: '/fleet/usage', label: 'Equipment Usage' },
    { path: '/fleet/transfers', label: 'Transfers' },
    { path: '/fleet/checkin', label: 'Check In / Out' },
    { path: '/fleet/predictions', label: 'Predictions' },
    { path: '/fleet/notifications', label: 'Notifications' },
  ];

  return <DashboardLayout title="Fleet Manager" links={links} />;
};

export default FleetManagerLayout;
