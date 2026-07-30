import DashboardLayout from './DashboardLayout';

const DealerLayout = () => {
  const links = [
    { path: '/dealer/dashboard', label: 'Dashboard' },
    { path: '/dealer/machines', label: 'Machines' },
    { path: '/dealer/rentals', label: 'Rentals' },
    { path: '/dealer/maintenance', label: 'Maintenance' },
    { path: '/dealer/predictions', label: 'Predictions' },
    { path: '/dealer/notifications', label: 'Notifications' },
  ];

  return <DashboardLayout title="Dealer Portal" links={links} />;
};

export default DealerLayout;
