import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { rentalAPI } from '../../api';

const FleetCheckin = () => {
  const [actions, setActions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
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
    fetchActions();
  }, []);

  const columns = [
    { header: 'ID', accessor: 'id' },
    { header: 'Rental ID', accessor: 'rental_id' },
    { header: 'Action', accessor: 'action', 
      cell: (row) => (
        <span style={{
          padding: '0.2rem 0.5rem',
          borderRadius: '4px',
          fontSize: '0.8rem',
          background: row.action === 'CHECK_IN' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(239, 68, 68, 0.2)',
          color: row.action === 'CHECK_IN' ? '#10b981' : '#ef4444'
        }}>
          {row.action}
        </span>
      )
    },
    { 
      header: 'Timestamp', 
      accessor: 'timestamp',
      cell: (row) => new Date(row.timestamp).toLocaleString() 
    },
    { header: 'Performed By (User ID)', accessor: 'performed_by' },
    { header: 'Remarks', accessor: 'remarks', cell: (row) => row.remarks || '-' }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Physical Check-ins & Check-outs</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>RFID and QR scanning history for machine movement.</p>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading history...</div>
      ) : (
        <Table columns={columns} data={actions} />
      )}
    </div>
  );
};

export default FleetCheckin;
