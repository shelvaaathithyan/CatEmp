import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { rentalAPI, siteAPI } from '../../api';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'react-toastify';

const FleetTransfers = () => {
  const { user } = useAuth();
  const [transfers, setTransfers] = useState([]);
  const [activeRentals, setActiveRentals] = useState([]);
  const [availableSites, setAvailableSites] = useState([]);
  
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    rental_id: '',
    to_site_id: '',
    remarks: ''
  });

  const fetchData = async () => {
    try {
      // Fetch historical transfers
      const data = await rentalAPI.getTransfers();
      setTransfers(data);
      
      // Fetch active rentals to populate the dropdown
      const rentalsData = await rentalAPI.getAll({ rental_status: 'ACTIVE' });
      // A Fleet Manager only sees rentals for their site anyway
      setActiveRentals(rentalsData);
      
      // Fetch sites (now correctly returns all sites for the same customer)
      const sitesData = await siteAPI.getAll();
      setAvailableSites(sitesData);
    } catch (error) {
      console.error("Error fetching data:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Find the selected rental to extract equipment_id and from_site_id
    const selectedRental = activeRentals.find(r => r.id === parseInt(formData.rental_id));
    if (!selectedRental) {
      toast.error("Please select a valid machine.");
      return;
    }
    
    if (selectedRental.site_id === parseInt(formData.to_site_id)) {
      toast.warning("Machine is already at this destination site.");
      return;
    }

    try {
      const payload = {
        rental_id: selectedRental.id,
        equipment_id: selectedRental.equipment_id,
        from_site_id: selectedRental.site_id,
        to_site_id: parseInt(formData.to_site_id),
        transferred_by: user.id,
        remarks: formData.remarks
      };
      
      await rentalAPI.createTransfer(payload);
      toast.success("Machine successfully transferred!");
      setIsModalOpen(false);
      setFormData({ rental_id: '', to_site_id: '', remarks: '' });
      fetchData(); // Refresh all tables
    } catch (error) {
      toast.error("Failed to transfer machine. " + (error.response?.data?.detail || error.message));
    }
  };

  const columns = [
    { header: 'Transfer ID', accessor: 'id' },
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Rental ID', accessor: 'rental_id' },
    { header: 'From Site', accessor: 'from_site_id' },
    { header: 'To Site', accessor: 'to_site_id' },
    { 
      header: 'Date', 
      accessor: 'transfer_date',
      render: (val) => new Date(val).toLocaleString() 
    },
    { header: 'Remarks', accessor: 'remarks' }
  ];

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>Machine Transfers</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>History of machines moved between sites.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          style={{
            background: 'var(--primary)',
            color: 'white',
            border: 'none',
            padding: '0.75rem 1.5rem',
            borderRadius: '8px',
            fontSize: '1rem',
            fontWeight: '600',
            cursor: 'pointer',
            transition: 'opacity 0.2s'
          }}
          onMouseOver={e => e.target.style.opacity = '0.9'}
          onMouseOut={e => e.target.style.opacity = '1'}
        >
          Transfer Machine
        </button>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading transfer history...</div>
      ) : (
        <Table columns={columns} data={transfers} />
      )}

      {/* Premium Transfer Modal */}
      {isModalOpen && (
        <div style={{
          position: 'fixed',
          top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)',
          backdropFilter: 'blur(4px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            background: 'var(--surface)',
            padding: '2.5rem',
            borderRadius: '16px',
            width: '100%',
            maxWidth: '550px',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)',
            border: '1px solid var(--border)'
          }}>
            <h2 style={{ color: 'var(--text)', marginTop: 0, fontSize: '1.5rem', marginBottom: '1.5rem' }}>Initiate Transfer</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              
              <div>
                <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '500' }}>Select Machine to Transfer</label>
                <select 
                  name="rental_id" 
                  value={formData.rental_id} 
                  onChange={handleChange} 
                  required
                  style={{ 
                    width: '100%', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border)', 
                    background: 'var(--background)', color: 'var(--text)', fontSize: '1rem', cursor: 'pointer' 
                  }}
                >
                  <option value="" disabled>-- Choose a machine --</option>
                  {activeRentals.map(r => (
                    <option key={r.id} value={r.id}>
                      {r.equipment_id} (Rental #{r.id}) - Currently at Site {r.site_id}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '500' }}>Destination Site</label>
                <select 
                  name="to_site_id" 
                  value={formData.to_site_id} 
                  onChange={handleChange} 
                  required
                  style={{ 
                    width: '100%', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border)', 
                    background: 'var(--background)', color: 'var(--text)', fontSize: '1rem', cursor: 'pointer' 
                  }}
                >
                  <option value="" disabled>-- Choose destination site --</option>
                  {availableSites.map(s => (
                    <option key={s.id} value={s.id}>
                      {s.location} (ID: {s.id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ display: 'block', color: 'var(--text-secondary)', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '500' }}>Remarks (Optional)</label>
                <input 
                  type="text" 
                  name="remarks" 
                  value={formData.remarks} 
                  onChange={handleChange}
                  placeholder="e.g. Moved for emergency excavation"
                  style={{ 
                    width: '100%', padding: '0.85rem', borderRadius: '8px', border: '1px solid var(--border)', 
                    background: 'var(--background)', color: 'var(--text)', fontSize: '1rem' 
                  }} 
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1.5rem' }}>
                <button type="button" onClick={() => setIsModalOpen(false)}
                  style={{ 
                    padding: '0.85rem 1.5rem', background: 'transparent', color: 'var(--text)', 
                    border: '1px solid var(--border)', borderRadius: '8px', cursor: 'pointer', fontWeight: '500' 
                  }}>
                  Cancel
                </button>
                <button type="submit"
                  style={{ 
                    padding: '0.85rem 1.5rem', background: 'var(--primary)', color: 'white', 
                    border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '600',
                    boxShadow: '0 4px 6px -1px rgba(250, 204, 21, 0.2)' 
                  }}>
                  Submit Transfer
                </button>
              </div>

            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetTransfers;
