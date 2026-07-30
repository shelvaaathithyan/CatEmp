import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { rentalAPI, operatorAPI } from '../../api';
import { useAuth } from '../../context/AuthContext';
import { Html5QrcodeScanner, Html5Qrcode } from 'html5-qrcode';

const FleetCheckin = () => {
  const { user } = useAuth();
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  
  // Form state
  const [equipmentId, setEquipmentId] = useState('');
  const [actionType, setActionType] = useState('CHECK_IN');
  const [remarks, setRemarks] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [scanError, setScanError] = useState('');

  // Operator fields
  const [operatorName, setOperatorName] = useState('');
  const [operatorId, setOperatorId] = useState('');
  const [existingOperators, setExistingOperators] = useState([]);
  const [useExisting, setUseExisting] = useState(false);
  const [selectedOperatorId, setSelectedOperatorId] = useState('');

  const fetchActions = async () => {
    try {
      const data = await rentalAPI.getCheckins();
      setActions(data);
    } catch (error) {
      console.error("Error fetching check-ins:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchActions();
    // Load existing operators for the dropdown
    const loadOperators = async () => {
      try {
        const ops = await operatorAPI.getAll();
        setExistingOperators(ops);
      } catch (e) {
        console.error("Could not load operators:", e);
      }
    };
    loadOperators();
  }, []);

  // Initialize QR Scanner when modal opens
  useEffect(() => {
    if (showModal) {
      const timer = setTimeout(() => {
        const readerEl = document.getElementById("reader");
        if (!readerEl) return;
        const scanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: {width: 250, height: 250} }, false);
        scanner.render(
          (decodedText) => {
            setEquipmentId(decodedText);
            scanner.clear();
          },
          (error) => {
            // ignoring continuous errors
          }
        );
        // Store ref for cleanup
        readerEl._scanner = scanner;
      }, 100);
      return () => {
        clearTimeout(timer);
        const readerEl = document.getElementById("reader");
        if (readerEl && readerEl._scanner) {
          readerEl._scanner.clear().catch(error => console.error("Failed to clear scanner", error));
        }
      };
    }
  }, [showModal]);

  const handleFileUpload = async (e) => {
    if (e.target.files && e.target.files.length > 0) {
      const file = e.target.files[0];
      const html5QrCode = new Html5Qrcode("reader-upload");
      try {
        const decodedText = await html5QrCode.scanFile(file, true);
        setEquipmentId(decodedText);
        setScanError('');
      } catch (err) {
        setScanError('Could not read QR code from this image. Try again or enter the ID manually.');
      }
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!equipmentId) return;
    setSubmitting(true);
    try {
      // Find the active rental for this equipment
      const rentals = await rentalAPI.getAll({ rental_status: 'ACTIVE' });
      const activeRental = rentals.find(r => r.equipment_id === equipmentId);
      
      if (!activeRental) {
        alert("No active rental found for equipment: " + equipmentId);
        setSubmitting(false);
        return;
      }

      // If CHECK_IN, handle operator assignment
      if (actionType === 'CHECK_IN') {
        if (useExisting && selectedOperatorId) {
          // Use existing operator — no creation needed
        } else if (operatorName && operatorId) {
          // Create new operator
          try {
            await operatorAPI.create({
              operator_id: operatorId,
              operator_name: operatorName,
              customer_id: activeRental.customer_id
            });
          } catch (err) {
            // If it already exists, that's fine
            if (!err.response?.data?.detail?.includes('already exists')) {
              console.error("Operator create failed:", err);
            }
          }
        }
      }

      // Submit the check-in/out action
      await rentalAPI.checkinCheckout({
        rental_id: activeRental.id,
        action: actionType,
        performed_by: user.id,
        remarks: remarks || (actionType === 'CHECK_IN' 
          ? `Operator: ${useExisting ? selectedOperatorId : operatorId || 'N/A'}` 
          : "Equipment returned")
      });
      
      // Reset and close
      setShowModal(false);
      setEquipmentId('');
      setRemarks('');
      setOperatorName('');
      setOperatorId('');
      setUseExisting(false);
      setSelectedOperatorId('');
      fetchActions();
      // Reload operators
      const ops = await operatorAPI.getAll();
      setExistingOperators(ops);
    } catch (err) {
      alert("Error logging action: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const columns = [
    { header: 'ID', accessor: 'id' },
    { header: 'Rental ID', accessor: 'rental_id' },
    { header: 'Action', accessor: 'action', 
      cell: (row) => (
        <span style={{
          padding: '0.25rem 0.75rem',
          borderRadius: '20px',
          fontSize: '0.8rem',
          fontWeight: '700',
          background: row.action === 'CHECK_IN' ? 'rgba(16, 185, 129, 0.15)' : 'rgba(239, 68, 68, 0.15)',
          color: row.action === 'CHECK_IN' ? '#10b981' : '#ef4444'
        }}>
          {row.action === 'CHECK_IN' ? '↓ CHECK IN' : '↑ CHECK OUT'}
        </span>
      )
    },
    { 
      header: 'Timestamp', 
      accessor: 'timestamp',
      cell: (row) => new Date(row.timestamp).toLocaleString() 
    },
    { header: 'Performed By', accessor: 'performed_by' },
    { header: 'Remarks', accessor: 'remarks', cell: (row) => row.remarks || '-' }
  ];

  const inputStyle = {
    width: '100%', padding: '0.75rem', borderRadius: '8px',
    border: '1px solid var(--border)', background: 'var(--background)',
    color: 'var(--text)', fontSize: '1rem'
  };

  const labelStyle = {
    display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem',
    fontWeight: '600', color: 'var(--text-secondary)'
  };

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Physical Check-ins & Check-outs</h1>
          <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>QR scanning and operator assignment for machine movement.</p>
        </div>
        <button 
          onClick={() => setShowModal(true)}
          style={{
            background: 'var(--primary)', color: 'var(--black)', padding: '0.8rem 1.5rem',
            border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer',
            fontSize: '1rem', boxShadow: '0 4px 6px -1px rgba(250, 204, 21, 0.2)'
          }}
        >
          + Log New Action
        </button>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading history...</div>
      ) : (
        <Table columns={columns} data={actions} />
      )}

      {/* Check-In / Check-Out Modal */}
      {showModal && (
        <div style={{
          position: 'fixed', top: 0, left: 0, width: '100%', height: '100%',
          background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(4px)',
          display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000
        }}>
          <div style={{
            background: 'var(--surface, white)', padding: '2.5rem', borderRadius: '16px',
            width: '520px', maxHeight: '90vh', overflowY: 'auto',
            boxShadow: '0 25px 50px -12px rgba(0,0,0,0.25)', border: '1px solid var(--border)'
          }}>
            <h2 style={{ marginTop: 0, marginBottom: '1.5rem', fontSize: '1.5rem', color: 'var(--text)' }}>
              Log Machine Action
            </h2>
            
            {/* QR Scanner */}
            <div id="reader" style={{ width: '100%', marginBottom: '1rem' }}></div>
            <div id="reader-upload" style={{ display: 'none' }}></div>
            
            <div style={{ marginBottom: '1.25rem' }}>
              <label style={labelStyle}>Or Upload QR Image</label>
              <input type="file" accept="image/*" onChange={handleFileUpload} />
              {scanError && <p style={{ color: '#e74c3c', fontSize: '0.8rem', marginTop: '0.5rem' }}>{scanError}</p>}
            </div>
            
            <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
              {/* Equipment ID */}
              <div>
                <label style={labelStyle}>Equipment ID</label>
                <input 
                  type="text" value={equipmentId} 
                  onChange={(e) => setEquipmentId(e.target.value)}
                  placeholder="Scanned or enter manually (e.g. EX-001)"
                  style={inputStyle} required
                />
              </div>

              {/* Action Type */}
              <div>
                <label style={labelStyle}>Action</label>
                <select 
                  value={actionType} onChange={(e) => setActionType(e.target.value)}
                  style={{ ...inputStyle, cursor: 'pointer' }}
                >
                  <option value="CHECK_IN">↓ Check In (Machine arrived at site)</option>
                  <option value="CHECK_OUT">↑ Check Out (Machine leaving site)</option>
                </select>
              </div>

              {/* Operator Details - Only visible on CHECK_IN */}
              {actionType === 'CHECK_IN' && (
                <div style={{
                  background: 'rgba(250, 204, 21, 0.08)', border: '1px solid rgba(250, 204, 21, 0.3)',
                  borderRadius: '12px', padding: '1.25rem'
                }}>
                  <h3 style={{ margin: '0 0 1rem 0', fontSize: '1rem', color: 'var(--text)' }}>
                    👷 Assign Operator
                  </h3>
                  
                  <div style={{ marginBottom: '1rem' }}>
                    <label style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }}>
                      <input 
                        type="checkbox" checked={useExisting} 
                        onChange={(e) => setUseExisting(e.target.checked)}
                      />
                      <span style={{ fontSize: '0.9rem', color: 'var(--text)' }}>Use existing operator</span>
                    </label>
                  </div>

                  {useExisting ? (
                    <div>
                      <label style={labelStyle}>Select Operator</label>
                      <select 
                        value={selectedOperatorId} 
                        onChange={(e) => setSelectedOperatorId(e.target.value)}
                        style={{ ...inputStyle, cursor: 'pointer' }}
                        required
                      >
                        <option value="" disabled>-- Choose operator --</option>
                        {existingOperators.map(op => (
                          <option key={op.operator_id} value={op.operator_id}>
                            {op.operator_name} ({op.operator_id})
                          </option>
                        ))}
                      </select>
                    </div>
                  ) : (
                    <>
                      <div style={{ marginBottom: '1rem' }}>
                        <label style={labelStyle}>Operator Name</label>
                        <input 
                          type="text" value={operatorName} 
                          onChange={(e) => setOperatorName(e.target.value)}
                          placeholder="e.g. John Doe"
                          style={inputStyle} required
                        />
                      </div>
                      <div>
                        <label style={labelStyle}>Operator ID</label>
                        <input 
                          type="text" value={operatorId} 
                          onChange={(e) => setOperatorId(e.target.value)}
                          placeholder="e.g. OP-005"
                          style={inputStyle} required
                        />
                      </div>
                    </>
                  )}
                </div>
              )}

              {/* Remarks */}
              <div>
                <label style={labelStyle}>Remarks (Optional)</label>
                <input 
                  type="text" value={remarks} 
                  onChange={(e) => setRemarks(e.target.value)}
                  placeholder="e.g. Machine arrived in good condition"
                  style={inputStyle}
                />
              </div>

              {/* Buttons */}
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '0.5rem' }}>
                <button 
                  type="button" 
                  onClick={() => { setShowModal(false); setEquipmentId(''); }}
                  style={{
                    padding: '0.85rem 1.5rem', background: 'transparent', color: 'var(--text)',
                    border: '1px solid var(--border)', borderRadius: '8px', cursor: 'pointer', fontWeight: '500'
                  }}
                >
                  Cancel
                </button>
                <button 
                  type="submit" disabled={submitting || !equipmentId}
                  style={{
                    padding: '0.85rem 1.5rem', background: 'var(--primary)', color: 'var(--black)',
                    border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '700',
                    boxShadow: '0 4px 6px -1px rgba(250, 204, 21, 0.2)',
                    opacity: (submitting || !equipmentId) ? 0.6 : 1
                  }}
                >
                  {submitting ? 'Submitting...' : 'Submit Action'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default FleetCheckin;
