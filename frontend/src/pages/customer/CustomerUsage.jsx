import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { usageAPI } from '../../api';

const CustomerUsage = () => {
  const [usageLogs, setUsageLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const data = await usageAPI.getAll();
        setUsageLogs(data);
      } catch (error) {
        console.error("Error fetching usage logs:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchUsage();
  }, []);

  const columns = [
    { header: 'Date', accessor: 'usage_date' },
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Site ID', accessor: 'site_id' },
    { header: 'Engine Hours', accessor: 'engine_hours_per_day' },
    { header: 'Idle Hours', accessor: 'idle_hours_per_day' },
    { header: 'Operator', accessor: 'last_operator_id' }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>Equipment Usage</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Track daily usage logs and engine hours for your rentals.</p>
      </div>

      <Card>
        {loading ? (
          <div style={{ color: 'var(--text)' }}>Loading usage logs...</div>
        ) : (
          <Table columns={columns} data={usageLogs} />
        )}
      </Card>
    </div>
  );
};

export default CustomerUsage;
