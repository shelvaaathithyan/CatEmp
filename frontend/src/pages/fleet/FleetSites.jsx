import React, { useState, useEffect } from 'react';
import Table from '../../components/common/Table';
import { siteAPI } from '../../api';

const FleetSites = () => {
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchSites = async () => {
      try {
        const data = await siteAPI.getAll();
        setSites(data);
      } catch (error) {
        console.error("Error fetching sites:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchSites();
  }, []);

  const columns = [
    { header: 'Site ID', accessor: 'id' },
    { header: 'Location', accessor: 'location' },
    { header: 'Customer ID', accessor: 'customer_id' }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>My Assigned Site</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>View details about the location you are managing.</p>
      </div>
      
      {loading ? (
        <div style={{ color: 'var(--text)' }}>Loading site data...</div>
      ) : (
        <Table columns={columns} data={sites} />
      )}
    </div>
  );
};

export default FleetSites;
