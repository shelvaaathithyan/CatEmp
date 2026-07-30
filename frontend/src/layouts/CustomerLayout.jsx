import DashboardLayout from './DashboardLayout';

const CustomerLayout = () => {
  const links = [
    { path: '/customer/dashboard', label: 'Dashboard' },
    { path: '/customer/sites', label: 'Sites' },
    { path: '/customer/rentals', label: 'Rentals' },
    { path: '/customer/operators', label: 'Operators' },
    { path: '/customer/usage', label: 'Equipment Usage' },
    { path: '/customer/predictions', label: 'Predictions' },
    { path: '/customer/notifications', label: 'Notifications' },
  ];

  return <DashboardLayout title="Customer Portal" links={links} />;
};

export default CustomerLayout;
