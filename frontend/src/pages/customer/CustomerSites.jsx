import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { siteAPI } from '../../api';

const CustomerSites = () => {
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
    { header: 'Site Code', accessor: 'site_code' },
    { 
      header: 'Site Name', 
      accessor: 'site_name',
      cell: (row) => <span style={{ fontWeight: 'bold' }}>{row.site_name}</span>
    },
    { header: 'Location', accessor: 'location' },
    {
      header: 'Fleet Managers',
      accessor: 'fleet_managers',
      cell: (row) => {
        if (!row.fleet_managers || row.fleet_managers.length === 0) {
          return <span style={{ color: 'var(--text-secondary)' }}>None Assigned</span>;
        }
        return (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.25rem' }}>
            {row.fleet_managers.map(fm => (
              <span key={fm.id} style={{ fontSize: '0.9rem' }}>
                {fm.user.name} <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem' }}>({fm.user.email})</span>
              </span>
            ))}
          </div>
        );
      }
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>My Sites</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Manage your active work sites.</p>
      </div>

      <Card>
        {loading ? (
          <div style={{ color: 'var(--text)' }}>Loading sites...</div>
        ) : (
          <Table columns={columns} data={sites} />
        )}
      </Card>
    </div>
  );
};

export default CustomerSites;
