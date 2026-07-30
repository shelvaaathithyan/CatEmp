import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { predictionAPI } from '../../api';

const CustomerPredictions = () => {
  const [activeTab, setActiveTab] = useState('maintenance');
  const [maintenance, setMaintenance] = useState([]);
  const [utilization, setUtilization] = useState([]);
  const [anomaly, setAnomaly] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [maintData, utilData, anomalyData] = await Promise.all([
          predictionAPI.getMaintenance(),
          predictionAPI.getUtilization(),
          predictionAPI.getAnomaly()
        ]);
        setMaintenance(maintData);
        setUtilization(utilData);
        setAnomaly(anomalyData);
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

  const maintenanceColumns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Model', accessor: 'model', cell: (row) => <span style={{ fontWeight: '600', color: 'var(--black)' }}>{row.model ? `CAT ${row.model}` : row.equipment_type || 'N/A'}</span> },
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

  const utilizationColumns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Model', accessor: 'model', cell: (row) => <span style={{ fontWeight: '600', color: 'var(--black)' }}>{row.model ? `CAT ${row.model}` : row.equipment_type || 'N/A'}</span> },
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

  const anomalyColumns = [
    { header: 'Equipment ID', accessor: 'equipment_id' },
    { header: 'Model', accessor: 'model', cell: (row) => <span style={{ fontWeight: '600', color: 'var(--black)' }}>{row.model ? `CAT ${row.model}` : row.equipment_type || 'N/A'}</span> },
    {
      header: 'Anomaly Status',
      accessor: 'anomaly_status',
      cell: (row) => {
        const isAnomaly = row.anomaly_status === 'Anomaly';
        return (
          <span style={{
            background: isAnomaly ? '#e74c3c20' : '#27ae6020',
            color: isAnomaly ? '#e74c3c' : '#27ae60',
            padding: '4px 12px', borderRadius: '20px', fontWeight: '700', fontSize: '0.8rem'
          }}>
            {row.anomaly_status}
          </span>
        );
      }
    },
    {
      header: 'Anomaly Score',
      accessor: 'anomaly_score',
      cell: (row) => {
        const score = parseFloat(row.anomaly_score || 0);
        const pct = (score * 100).toFixed(0);
        const color = score >= 0.7 ? '#e74c3c' : score >= 0.4 ? '#f39c12' : '#27ae60';
        return (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
            <div style={{ width: '80px', height: '8px', background: '#eee', borderRadius: '4px', overflow: 'hidden' }}>
              <div style={{ width: `${pct}%`, height: '100%', background: color, borderRadius: '4px' }} />
            </div>
            <span style={{ fontWeight: '600', color }}>{pct}%</span>
          </div>
        );
      }
    },
    {
      header: 'Severity',
      accessor: 'severity',
      cell: (row) => {
        const sev = row.severity || 'N/A';
        const color = sev === 'HIGH' ? '#e74c3c' : sev === 'MEDIUM' ? '#f39c12' : '#27ae60';
        return (
          <span style={{
            background: color + '20', color: color,
            padding: '4px 12px', borderRadius: '20px', fontWeight: '700', fontSize: '0.8rem'
          }}>
            {sev}
          </span>
        );
      }
    },
    {
      header: 'Timestamp',
      accessor: 'prediction_timestamp',
      cell: (row) => new Date(row.prediction_timestamp).toLocaleString()
    }
  ];

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Predictions</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>AI-driven maintenance, utilization, and anomaly forecasts for your rented equipment.</p>
      </div>

      <div style={{ display: 'flex', borderBottom: '1px solid var(--border)', marginBottom: '1.5rem' }}>
        <button style={tabStyle('maintenance')} onClick={() => setActiveTab('maintenance')}>Maintenance</button>
        <button style={tabStyle('utilization')} onClick={() => setActiveTab('utilization')}>Utilization</button>
        <button style={tabStyle('anomaly')} onClick={() => setActiveTab('anomaly')}>Anomaly Detection</button>
      </div>

      {loading ? (
        <Card><div style={{ padding: '2rem', color: 'var(--medium)' }}>Loading predictions...</div></Card>
      ) : (
        <>
          {activeTab === 'maintenance' && (
            <Card title="Maintenance Forecasts">
              {maintenance.length > 0 ? (
                <Table columns={maintenanceColumns} data={maintenance} />
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--medium)' }}>No maintenance predictions available yet.</div>
              )}
            </Card>
          )}

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
            <Card title="Anomaly Detection & Alerts">
              {anomaly.length > 0 ? (
                <Table columns={anomalyColumns} data={anomaly} />
              ) : (
                <div style={{ padding: '2rem', textAlign: 'center', color: 'var(--medium)' }}>No anomaly data available yet.</div>
              )}
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default CustomerPredictions;
