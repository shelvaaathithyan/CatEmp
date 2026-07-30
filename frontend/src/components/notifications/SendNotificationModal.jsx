import { useState, useEffect } from 'react';
import { X, Send } from 'lucide-react';
import { toast } from 'react-toastify';
import api from '../../api';

const SendNotificationModal = ({ isOpen, onClose }) => {
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    recipient_id: '',
    title: '',
    message: '',
    priority: 'INFO'
  });

  useEffect(() => {
    if (isOpen) {
      fetchNetwork();
    }
  }, [isOpen]);

  const fetchNetwork = async () => {
    try {
      const res = await api.get('/auth/network');
      setRecipients(res.data);
    } catch (err) {
      console.error(err);
      toast.error('Failed to load network users.');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!formData.recipient_id || !formData.title || !formData.message) {
      toast.warning('Please fill in all required fields.');
      return;
    }
    setLoading(true);
    try {
      await api.post('/notifications/send', {
        ...formData,
        recipient_id: parseInt(formData.recipient_id, 10),
        notification_type: 'MANUAL'
      });
      toast.success('Notification sent successfully!');
      onClose();
      setFormData({ recipient_id: '', title: '', message: '', priority: 'INFO' });
    } catch (err) {
      console.error(err);
      toast.error('Failed to send notification.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh',
      backgroundColor: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center',
      justifyContent: 'center', zIndex: 9999
    }}>
      <div style={{
        background: 'var(--card)', borderRadius: '12px', padding: '2rem',
        width: '500px', maxWidth: '90%', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1)',
        border: '1px solid var(--border)'
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
          <h2 style={{ fontFamily: 'var(--font-heading)', color: 'var(--black)', fontSize: '1.5rem', fontWeight: '800' }}>Send Notification</h2>
          <button onClick={onClose} style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--medium)' }}>
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: 'var(--black)', fontSize: '0.875rem' }}>Recipient</label>
            <select 
              value={formData.recipient_id} 
              onChange={e => setFormData({...formData, recipient_id: e.target.value})}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', fontFamily: 'var(--font-body)', fontSize: '0.95rem' }}
            >
              <option value="">Select a recipient...</option>
              {recipients.map(user => (
                <option key={user.id} value={user.id}>{user.name} ({user.role})</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: 'var(--black)', fontSize: '0.875rem' }}>Priority</label>
            <select 
              value={formData.priority} 
              onChange={e => setFormData({...formData, priority: e.target.value})}
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', fontFamily: 'var(--font-body)', fontSize: '0.95rem' }}
            >
              <option value="INFO">Information</option>
              <option value="WARNING">Warning</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: 'var(--black)', fontSize: '0.875rem' }}>Title</label>
            <input 
              type="text" 
              value={formData.title} 
              onChange={e => setFormData({...formData, title: e.target.value})}
              placeholder="E.g., Missing paperwork for site transfer"
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', fontFamily: 'var(--font-body)', fontSize: '0.95rem' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '600', color: 'var(--black)', fontSize: '0.875rem' }}>Message</label>
            <textarea 
              rows="4"
              value={formData.message} 
              onChange={e => setFormData({...formData, message: e.target.value})}
              placeholder="Enter your message..."
              style={{ width: '100%', padding: '0.75rem', borderRadius: '8px', border: '1px solid var(--border)', fontFamily: 'var(--font-body)', fontSize: '0.95rem', resize: 'vertical' }}
            />
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '1rem' }}>
            <button 
              type="submit" 
              disabled={loading}
              style={{ 
                background: 'var(--primary)', color: 'var(--black)', fontWeight: '700', 
                padding: '0.75rem 1.5rem', borderRadius: '8px', border: 'none', cursor: 'pointer',
                display: 'flex', alignItems: 'center', gap: '0.5rem'
              }}
            >
              {loading ? 'Sending...' : <><Send size={18} /> Send</>}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SendNotificationModal;
