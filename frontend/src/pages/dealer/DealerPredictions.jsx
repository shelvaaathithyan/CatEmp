import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { predictionAPI } from '../../api';

const DealerPredictions = () => {
  const [activeTab, setActiveTab] = useState('demand');
  const [demand, setDemand] = useState([]);
  const [maintenance, setMaintenance] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [demandData, maintData] = await Promise.all([
          predictionAPI.getDemand(),
          predictionAPI.getMaintenance()
        ]);
        setDemand(demandData);
        setMaintenance(maintData);
      } catch (err) {
        console.error('Failed to fetch predictions:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const tabStyle = (tab) => ({
    padding: '0.75rem 1.5rem',
    border: 'none',
    borderBottom: activeTab === tab ? '3px solid var(--primary)' : '3px solid transparent',
    background: 'none',
    cursor: 'pointer',
    fontWeight: activeTab === tab ? '700' : '500',
    color: activeTab === tab ? 'var(--black)' : 'var(--medium)',
    fontFamily: 'var(--font-body)',
    fontSize: '1rem',
    transition: 'all 0.2s ease'
  });

  const demandColumns = [
    { header: 'Equipment Type', accessor: 'equipment_type' },
    { header: 'Site ID', accessor: 'site_id' },
    { header: 'Period', accessor: 'prediction_period' },
    {
      header: 'Expected Demand',
      accessor: 'expected_demand',
      cell: (row) => {
        const demand = row.expected_demand;
        const color = demand >= 5 ? '#e74c3c' : demand >= 3 ? '#f39c12' : '#27ae60';
        return (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <span style={{
              background: color + '20', color: color, padding: '4px 16px',
              borderRadius: '20px', fontWeight: '700', fontSize: '0.9rem'
            }}>
              {demand} units
            </span>
          </div>
        );
      }
    },
    {
      header: 'Timestamp',
      accessor: 'prediction_timestamp',
      cell: (row) => new Date(row.prediction_timestamp).toLocaleDateString()
    }
  ];

  const maintenanceColumns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    {
      header: 'Risk Level',
      accessor: 'maintenance_probability',
      cell: (row) => {
        const prob = parseFloat(row.maintenance_probability);
        const color = prob >= 0.7 ? '#e74c3c' : prob >= 0.4 ? '#f39c12' : '#27ae60';
        const label = prob >= 0.7 ? 'HIGH' : prob >= 0.4 ? 'MEDIUM' : 'LOW';
        return (
          <span style={{
            background: color + '20', color: color, padding: '4px 12px',
            borderRadius: '20px', fontWeight: '700', fontSize: '0.8rem'
          }}>
            {label} ({(prob * 100).toFixed(0)}%)
          </span>
        );
      }
    },
    {
      header: 'Predicted Service Date',
      accessor: 'predicted_service_date',
      cell: (row) => new Date(row.predicted_service_date).toLocaleDateString()
    },
    {
      header: 'Confidence',
      accessor: 'confidence',
      cell: (row) => `${(parseFloat(row.confidence) * 100).toFixed(0)}%`
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Predictions</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>AI-driven demand forecasts and maintenance predictions for your machine fleet.</p>
      </div>

      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
        <button style={tabStyle('demand')} onClick={() => setActiveTab('demand')}>Demand Forecast</button>
        <button style={tabStyle('maintenance')} onClick={() => setActiveTab('maintenance')}>Maintenance</button>
      </div>

      {loading ? (
        <Card><div style={{ padding: '2rem', color: 'var(--medium)' }}>Loading predictions...</div></Card>
      ) : (
        <>
          {activeTab === 'demand' && (
            <Card title="Demand Predictions">
              {demand.length > 0 ? (
                <Table columns={demandColumns} data={demand} />
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--medium)' }}>No demand predictions available yet.</div>
              )}
            </Card>
          )}

          {activeTab === 'maintenance' && (
            <Card title="Maintenance Forecasts">
              {maintenance.length > 0 ? (
                <Table columns={maintenanceColumns} data={maintenance} />
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--medium)' }}>No maintenance predictions available yet.</div>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default DealerPredictions;
