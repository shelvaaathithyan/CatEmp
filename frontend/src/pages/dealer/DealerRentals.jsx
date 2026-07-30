import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { rentalAPI } from '../../api';

const DealerRentals = () => {
  const [rentals, setRentals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchRentals = async () => {
      try {
        const data = await rentalAPI.getAll();
        setRentals(data);
      } catch (error) {
        console.error("Error fetching rentals:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchRentals();
  }, []);

  const columns = [
    { header: 'Rental ID', accessor: 'id' },
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Customer ID', accessor: 'customer_id' },
    { header: 'Site ID', accessor: 'site_id' },
    { header: 'Expected Return', accessor: 'expected_return_date' },
    { 
      header: 'Status', 
      accessor: 'rental_status',
      cell: (row) => {
        let color = 'var(--text)';
        if (row.rental_status === 'ACTIVE') color = 'var(--success)';
        if (row.rental_status === 'PENDING') color = 'var(--warning)';
        if (row.rental_status === 'COMPLETED') color = 'var(--text-secondary)';
        
        return <span style={{ color, fontWeight: 'bold' }}>{row.rental_status}</span>;
      }
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Rental Contracts</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Track all active and past rentals for your fleet.</p>
      </div>

      <Card>
        {loading ? (
          <div style={{ color: 'var(--text)' }}>Loading rentals...</div>
        ) : (
          <Table columns={columns} data={rentals} />
        )}
      </Card>
    </div>
  );
};

export default DealerRentals;
