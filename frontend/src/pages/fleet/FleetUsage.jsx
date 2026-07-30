import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { usageAPI } from '../../api';

const FleetUsage = () => {
  const [usageLogs, setUsageLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUsage = async () => {
      try {
        const data = await usageAPI.getAll();
        setUsageLogs(data);
      } catch (error) {
        console.error("Error fetching usage:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchUsage();
  }, []);

  const columns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Rental ID', accessor: 'rental_id' },
    { header: 'Date', accessor: 'usage_date' },
    { header: 'Engine Hours', accessor: 'engine_hours_per_day', cell: (row) => `${parseFloat(row.engine_hours_per_day).toFixed(1)}h` },
    { header: 'Idle Hours', accessor: 'idle_hours_per_day', cell: (row) => `${parseFloat(row.idle_hours_per_day).toFixed(1)}h` },
    { header: 'Operator ID', accessor: 'last_operator_id', cell: (row) => row.last_operator_id || 'N/A' }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Equipment Usage</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Daily operation logs for machines at your site.</p>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading usage logs...</div>
      ) : (
        <Table columns={columns} data={usageLogs} />
      )}
    </div>
  );
};

export default FleetUsage;
