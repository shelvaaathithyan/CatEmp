import React from 'react';
import NotificationList from '../../components/notifications/NotificationList';

const CustomerNotifications = () => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>My Notifications</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Alerts about your rentals, overdue returns, and site transfers.</p>
      </div>
      
      <NotificationList />
    </div>
  );
};

export default CustomerNotifications;
