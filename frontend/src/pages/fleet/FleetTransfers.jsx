import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { rentalAPI } from '../../api';

const FleetTransfers = () => {
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransfers = async () => {
      try {
        const data = await rentalAPI.getTransfers();
        setTransfers(data);
      } catch (error) {
        console.error("Error fetching transfers:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchTransfers();
  }, []);

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
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>Machine Transfers</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>History of machines moved between sites.</p>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading transfer history...</div>
      ) : (
        <Table columns={columns} data={transfers} />
      )}
    </div>
  );
};

export default FleetTransfers;
