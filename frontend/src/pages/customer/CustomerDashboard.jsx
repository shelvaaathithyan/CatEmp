import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import { dashboardAPI } from '../../api';

const CustomerDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await dashboardAPI.getCustomerDashboard();
        setData(result);
      } catch (error) {
        console.error("Error fetching customer dashboard", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div style={{ color: 'var(--text)' }}>Loading dashboard...</div>;
  if (!data) return <div style={{ color: 'var(--error)' }}>Error loading dashboard.</div>;

  const renderWidgetMachines = (widgetData) => {
    if (!widgetData || !widgetData.machines || widgetData.machines.length === 0) return <p style={{color: 'var(--text-secondary)', fontSize: '0.9rem'}}>No machines</p>;
    return (
      <ul style={{ listStyleType: 'none', padding: 0, marginTop: '10px' }}>
        {widgetData.machines.slice(0, 3).map(m => (
          <li key={m.equipment_id} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
            <strong style={{ color: 'var(--text)' }}>{m.equipment_id}</strong> - {m.model}
          </li>
        ))}
        {widgetData.count > 3 && <li style={{ fontSize: '0.85rem', color: 'var(--accent)', marginTop: '8px', cursor: 'pointer' }}>+ {widgetData.count - 3} more...</li>}
      </ul>
    );
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>Customer Dashboard</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>Overview of your rented machines and sites.</p>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        <Card title="Monthly Rental Cost">
          <h2 style={{ fontSize: '2.5rem', margin: '10px 0', color: 'var(--primary)' }}>${data.total_rental_cost_this_month.toLocaleString()}</h2>
        </Card>

        <Card title="Active Contracts">
          <h2 style={{ fontSize: '2.5rem', margin: '10px 0', color: 'var(--text)' }}>{data.active_rentals}</h2>
        </Card>
        
        <Card title="Machines on Rent">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--success)' }}>{data.total_machines_rented.count}</h2>
          {renderWidgetMachines(data.total_machines_rented)}
        </Card>

        <Card title="Upcoming Returns">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--warning)' }}>{data.upcoming_returns.count}</h2>
          {renderWidgetMachines(data.upcoming_returns)}
        </Card>

        <Card title="Active Sites">
          <h2 style={{ fontSize: '2.5rem', margin: '10px 0', color: 'var(--text)' }}>{data.active_sites}</h2>
        </Card>
        
        <Card title="Registered Operators">
          <h2 style={{ fontSize: '2.5rem', margin: '10px 0', color: 'var(--text)' }}>{data.total_operators}</h2>
        </Card>
      </div>
    </div>
  );
};

export default CustomerDashboard;
