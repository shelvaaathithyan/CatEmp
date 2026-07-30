import React, { useState } from 'react';
import NotificationList from '../../components/notifications/NotificationList';
import SendNotificationModal from '../../components/notifications/SendNotificationModal';
import { useAuth } from '../../context/AuthContext';

const CustomerNotifications = () => {
    const [isModalOpen, setIsModalOpen] = useState(false);

    return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h1 style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)', margin: 0 }}>My Notifications</h1>
            <button 
                onClick={() => setIsModalOpen(true)}
                style={{ 
                    background: 'var(--black)', color: 'white', padding: '0.75rem 1.5rem', 
                    borderRadius: '8px', border: 'none', cursor: 'pointer', fontWeight: 'bold' 
                }}
            >
                + Compose Notification
            </button>
        </div>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)', marginBottom: '2rem' }}>Alerts about your rentals, overdue returns, and account activity.</p>
        
        <NotificationList />
        <SendNotificationModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} />
      </div>
    </div>
  );
};

export default CustomerNotifications;
