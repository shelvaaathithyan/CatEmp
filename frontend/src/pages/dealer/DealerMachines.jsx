import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { machineAPI } from '../../api';

const DealerMachines = () => {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMachines = async () => {
      try {
        // Fetch all machines owned by the dealer. 
        // We assume the backend uses the JWT to filter by dealer_id or we get everything if it's single-tenant demo.
        const data = await machineAPI.getAll();
        setMachines(data);
      } catch (error) {
        console.error("Error fetching machines:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMachines();
  }, []);

  const columns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Type', accessor: 'equipment_type' },
    { header: 'Model', accessor: 'model' },
    { header: 'Serial Number', accessor: 'serial_number' },
    { 
      header: 'Status', 
      accessor: 'status',
      cell: (row) => {
        let color = 'var(--text)';
        if (row.status === 'AVAILABLE') color = 'var(--text)';
        if (row.status === 'RENTED') color = 'var(--success)';
        if (row.status === 'MAINTENANCE') color = 'var(--warning)';
        
        return <span style={{ color, fontWeight: 'bold' }}>{row.status}</span>;
      }
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Fleet Inventory</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Manage all your registered machines.</p>
      </div>

      <Card>
        {loading ? (
          <div style={{ color: 'var(--text)' }}>Loading machines...</div>
        ) : (
          <Table columns={columns} data={machines} />
        )}
      </Card>
    </div>
  );
};

export default DealerMachines;
