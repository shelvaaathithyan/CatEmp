import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { predictionAPI } from '../../api';

const FleetPredictions = () => {
  const [activeTab, setActiveTab] = useState('utilization');
  const [utilization, setUtilization] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const utilData = await predictionAPI.getUtilization();
        setUtilization(utilData);
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

  const utilizationColumns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    {
      header: 'Utilization Score',
      accessor: 'utilization_score',
      cell: (row) => {
        const score = parseFloat(row.utilization_score);
        const pct = (score * 100).toFixed(0);
        const color = score >= 0.7 ? '#27ae60' : score >= 0.4 ? '#f39c12' : '#e74c3c';
        return (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '100px', height: '8px', background: '#eee', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '4px' }} />
            </div>
            <span style={{ fontWeight: '600', color }}>{pct}%</span>
          </div>
        );
      }
    },
    {
      header: 'Predicted Idle Hours',
      accessor: 'predicted_idle_hours',
      cell: (row) => `${parseFloat(row.predicted_idle_hours).toFixed(1)} hrs`
    },
    {
      header: 'Status',
      accessor: 'status',
      cell: (row) => {
        const isRunning = row.status === 'Running';
        return (
          <span style={{
            background: isRunning ? '#27ae6020' : '#e74c3c20',
            color: isRunning ? '#27ae60' : '#e74c3c',
            padding: '4px 12px', borderRadius: '20px', fontWeight: '700', fontSize: '0.8rem'
          }}>
            {row.status}
          </span>
        );
      }
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Predictions</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>AI-driven utilization and anomaly forecasts for equipment at your sites.</p>
      </div>

      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
        <button style={tabStyle('utilization')} onClick={() => setActiveTab('utilization')}>Utilization</button>
        <button style={tabStyle('anomaly')} onClick={() => setActiveTab('anomaly')}>Anomaly Detection</button>
      </div>

      {loading ? (
        <Card><div style={{ padding: '2rem', color: 'var(--medium)' }}>Loading predictions...</div></Card>
      ) : (
        <>
          {activeTab === 'utilization' && (
            <Card title="Utilization Predictions">
              {utilization.length > 0 ? (
                <Table columns={utilizationColumns} data={utilization} />
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--medium)' }}>No utilization predictions available yet.</div>
              )}
            </Card>
          )}

          {activeTab === 'anomaly' && (
            <Card title="Anomaly Detection">
              <div style={{ padding: '3rem', textAlign: 'center', color: 'var(--medium)', fontFamily: 'var(--font-body)' }}>
                <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔍</div>
                <h3 style={{ color: 'var(--black)', marginBottom: '0.5rem' }}>Coming Soon</h3>
                <p>Anomaly detection model is currently under development. Real-time anomaly alerts will appear here.</p>
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default FleetPredictions;
