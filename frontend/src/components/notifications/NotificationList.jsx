import React, { useState, useEffect } from 'react';
import Card from '../common/Card';
import { notificationAPI } from '../../api';
import { useWebSocket } from '../../contexts/WebSocketContext';

const NotificationList = () => {
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const { realtimeNotifications } = useWebSocket();

  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const history = await notificationAPI.getAll();
        setNotifications(history);
      } catch (error) {
        console.error("Error fetching historical notifications:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchHistory();
  }, []);

  // Merge realtime notifications from the WebSocket context
  // Realtime notifications don't strictly exist in our local `notifications` state yet 
  // until we refresh, so we derive the view by combining them.
  const displayList = [...realtimeNotifications, ...notifications];
  
  // Deduplicate by ID just in case
  const uniqueList = Array.from(new Map(displayList.map(item => [item.id, item])).values());
  // Sort descending by created_at (safely handling missing dates)
  uniqueList.sort((a, b) => new Date(b.created_at || Date.now()) - new Date(a.created_at || Date.now()));

  const handleMarkAsRead = async (id, currentReadStatus) => {
    if (currentReadStatus) return;
    try {
      await notificationAPI.markAsRead(id);
      // Update local state to reflect it's read
      setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n));
    } catch (e) {
      console.error("Failed to mark as read", e);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading notifications...</div>
      ) : uniqueList.length === 0 ? (
        <div style={{ color: 'var(--text-secondary)' }}>You have no notifications.</div>
      ) : (
        uniqueList.map(notif => (
          <Card key={notif.id} style={{ opacity: notif.is_read ? 0.6 : 1, transition: 'opacity 0.2s' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                  {notif.priority === 'HIGH' && <span style={{ background: '#ef4444', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold' }}>HIGH</span>}
                  {notif.priority === 'MEDIUM' && <span style={{ background: '#f59e0b', color: 'white', padding: '0.2rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 'bold' }}>MEDIUM</span>}
                  <h3 style={{ margin: 0, color: 'var(--text)' }}>{notif.title}</h3>
                </div>
                <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{notif.message}</p>
                {notif.equipment_id && (
                  <p style={{ margin: '0.5rem 0 0 0', fontSize: '0.85rem', color: 'var(--primary)' }}>Equipment: {notif.equipment_id}</p>
                )}
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '1rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  {new Date(notif.created_at).toLocaleString()}
                </span>
                {!notif.is_read && (
                  <button 
                    onClick={() => handleMarkAsRead(notif.id, notif.is_read)}
                    style={{
                      background: 'transparent',
                      border: '1px solid var(--border)',
                      color: 'var(--text)',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.8rem'
                    }}
                  >
                    Mark as read
                  </button>
                )}
              </div>
            </div>
          </Card>
        ))
      )}
    </div>
  );
};

export default NotificationList;
