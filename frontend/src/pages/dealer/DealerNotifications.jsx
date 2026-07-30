import React from 'react';
import NotificationList from '../../components/notifications/NotificationList';

const DealerNotifications = () => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>Alerts & Notifications</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Stay updated on maintenance flags and critical fleet events.</p>
      </div>
      
      <NotificationList />
    </div>
  );
};

export default DealerNotifications;
