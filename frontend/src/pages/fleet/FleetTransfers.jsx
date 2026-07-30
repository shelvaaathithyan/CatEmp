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
  const [siteLookup, setSiteLookup] = useState({});
  
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const [formData, setFormData] = useState({
    rental_id: '',
    to_site_id: '',
    remarks: ''
  });

  const fetchData = async () => {
    try {
      const [data, rentalsData, sitesData] = await Promise.all([
        rentalAPI.getTransfers(),
        rentalAPI.getAll({ rental_status: 'ACTIVE' }),
        siteAPI.getAll()
      ]);

      setTransfers(data);
      setActiveRentals(rentalsData);
      setAvailableSites(sitesData);

      // Build a lookup map: site_id -> site_name
      const lookup = {};
      sitesData.forEach(s => {
        lookup[s.id] = s.location || s.site_name || `Site ${s.id}`;
      });
      setSiteLookup(lookup);
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
      fetchData();
    } catch (error) {
      toast.error("Failed to transfer machine. " + (error.response?.data?.detail || error.message));
    }
  };

  const columns = [
    { header: 'Transfer ID', accessor: 'id' },
    { header: 'Equipment', accessor: 'equipment_id',
      cell: (row) => (
        <span style={{ fontWeight: '700', color: 'var(--black)' }}>
          {row.equipment_id}
        </span>
      )
    },
    { header: 'From Site', accessor: 'from_site_id',
      cell: (row) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            display: 'inline-block', width: '8px', height: '8px',
            borderRadius: '50%', background: '#e74c3c'
          }}/>
          {siteLookup[row.from_site_id] || `Site ${row.from_site_id}`}
        </span>
      )
    },
    { header: 'To Site', accessor: 'to_site_id',
      cell: (row) => (
        <span style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span style={{
            display: 'inline-block', width: '8px', height: '8px',
            borderRadius: '50%', background: '#27ae60'
          }}/>
          {siteLookup[row.to_site_id] || `Site ${row.to_site_id}`}
        </span>
      )
    },
    { 
      header: 'Transfer Date', 
      accessor: 'transfer_date',
      cell: (row) => new Date(row.transfer_date).toLocaleString() 
    },
    { header: 'Remarks', accessor: 'remarks', cell: (row) => row.remarks || '-' }
  ];

  const inputStyle = {
    width: '100%', padding: '0.85rem', borderRadius: '8px',
    border: '1px solid var(--border)', background: 'var(--background)',
    color: 'var(--text)', fontSize: '1rem', cursor: 'pointer'
  };

  const labelStyle = {
    display: 'block', color: 'var(--text-secondary)',
    marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: '600'
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Machine Transfers</h1>
          <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>History of machines moved between sites.</p>
        </div>
        <button 
          onClick={() => setIsModalOpen(true)}
          style={{
            background: 'var(--primary)', color: 'var(--black)', border: 'none',
            padding: '0.75rem 1.5rem', borderRadius: '8px', fontSize: '1rem',
            fontWeight: '700', cursor: 'pointer',
            boxShadow: '0 4px 6px -1px rgba(250, 204, 21, 0.2)',
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
      ) : transfers.length > 0 ? (
        <Table columns={columns} data={transfers} />
      ) : (
        <div style={{
          padding: '3rem', textAlign: 'center', background: 'var(--surface, white)',
          borderRadius: '12px', border: '1px solid var(--border)', color: 'var(--medium)'
        }}>
          <div style={{ fontSize: '2rem', marginBottom: '0.75rem' }}>🚛</div>
          <p>No transfers have been recorded yet.</p>
        </div>
      )}

      {/* Transfer Modal */}
      {isModalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
          <div style={{
            background: 'var(--surface, white)', padding: '2.5rem', borderRadius: '16px',
            width: '100%', maxWidth: '550px',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', border: '1px solid var(--border)'
          }}>
            <h2 style={{ color: 'var(--text)', marginTop: 0, fontSize: '1.5rem', marginBottom: '1.5rem' }}>Initiate Transfer</h2>
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              
              <div>
                <label style={labelStyle}>Select Machine to Transfer</label>
                <select 
                  name="rental_id" value={formData.rental_id} 
                  onChange={handleChange} required style={inputStyle}
                >
                  <option value="" disabled>-- Choose a machine --</option>
                  {activeRentals.map(r => (
                    <option key={r.id} value={r.id}>
                      {r.equipment_id} (Rental #{r.id}) — Currently at {siteLookup[r.site_id] || `Site ${r.site_id}`}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={labelStyle}>Destination Site</label>
                <select 
                  name="to_site_id" value={formData.to_site_id} 
                  onChange={handleChange} required style={inputStyle}
                >
                  <option value="" disabled>-- Choose destination site --</option>
                  {availableSites.map(s => (
                    <option key={s.id} value={s.id}>
                      {s.location || s.site_name || `Site ${s.id}`} (ID: {s.id})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label style={labelStyle}>Remarks (Optional)</label>
                <input 
                  type="text" name="remarks" value={formData.remarks} 
                  onChange={handleChange}
                  placeholder="e.g. Moved for emergency excavation"
                  style={{ ...inputStyle, cursor: 'text' }} 
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '1rem' }}>
                <button type="button" onClick={() => setIsModalOpen(false)}
                  style={{ 
                    padding: '0.85rem 1.5rem', background: 'transparent', color: 'var(--text)', 
                    border: '1px solid var(--border)', borderRadius: '8px', cursor: 'pointer', fontWeight: '500' 
                  }}>
                  Cancel
                </button>
                <button type="submit"
                  style={{ 
                    padding: '0.85rem 1.5rem', background: 'var(--primary)', color: 'var(--black)', 
                    border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '700',
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
