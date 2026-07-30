import React from 'react';
import NotificationList from '../../components/notifications/NotificationList';

const CustomerNotifications = () => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>My Notifications</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Alerts about your rentals, overdue returns, and site transfers.</p>
      </div>
      
      <NotificationList />
    </div>
  );
};

export default CustomerNotifications;
