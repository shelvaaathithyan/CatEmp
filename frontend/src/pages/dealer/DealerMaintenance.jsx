import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { machineAPI } from '../../api';

const DealerMaintenance = () => {
  const [machines, setMachines] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchMaintenanceMachines = async () => {
      try {
        const data = await machineAPI.getAll({ status: 'MAINTENANCE' });
        setMachines(data);
      } catch (error) {
        console.error("Error fetching maintenance machines:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchMaintenanceMachines();
  }, []);

  const columns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Type', accessor: 'equipment_type' },
    { header: 'Model', accessor: 'model' },
    { 
      header: 'Action Required', 
      accessor: 'status',
      cell: () => <span style={{ color: 'var(--warning)', fontWeight: 'bold' }}>Needs Service</span>
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Maintenance Logs</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Machines currently flagged for maintenance.</p>
      </div>

      <Card>
        {loading ? (
          <div style={{ color: 'var(--text)' }}>Loading maintenance data...</div>
        ) : (
          <Table columns={columns} data={machines} />
        )}
      </Card>
    </div>
  );
};

export default DealerMaintenance;
