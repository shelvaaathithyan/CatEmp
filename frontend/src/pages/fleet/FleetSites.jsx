import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { dashboardAPI } from '../../api';

const FleetSites = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSiteMachines = async () => {
      try {
        const dashboardData = await dashboardAPI.getFleetManagerDashboard();
        setData(dashboardData);
      } catch (error) {
        console.error("Error fetching site machines:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSiteMachines();
  }, []);

  const columns = [
    { header: 'Equipment ID', accessor: 'equipment_id', cell: (row) => <span style={{ fontWeight: 'bold' }}>{row.equipment_id}</span> },
    { header: 'Equipment Type', accessor: 'equipment_type' },
    { header: 'Model', accessor: 'model' },
    { header: 'Rental End Date', accessor: 'expected_return_date', cell: (row) => row.expected_return_date ? new Date(row.expected_return_date).toLocaleDateString() : 'N/A' }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Site Machines</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>
          {data ? `Machines currently stationed at ${data.assigned_site_name}` : "View machines at your assigned location."}
        </p>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading machines...</div>
      ) : data && data.active_machines && data.active_machines.machines.length > 0 ? (
        <Table 
          columns={columns} 
          data={data.active_machines.machines} 
        />
      ) : (
        <div style={{ padding: '2rem', background: 'var(--surface)', borderRadius: '12px', color: 'var(--text-secondary)' }}>
          No machines currently active at your site.
        </div>
      )}
    </div>
  );
};

export default FleetSites;
