import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import { dashboardAPI, notificationAPI } from '../../api';

const DealerDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await dashboardAPI.getDealerDashboard();
        setData(result);
      } catch (error) {
        console.error("Error fetching dealer dashboard", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) return <div style={{ color: 'var(--text)' }}>Loading dashboard...</div>;
  if (!data) return <div style={{ color: 'var(--error)' }}>Error loading dashboard.</div>;

  const renderWidgetMachines = (widgetData) => {
    if (!widgetData || !widgetData.machines || widgetData.machines.length === 0) return <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No machines in this category</p>;
    return (
      <ul style={{ listStyleType: 'none', padding: 0, marginTop: '10px' }}>
        {widgetData.machines.slice(0, 3).map(m => (
          <li key={m.equipment_id} style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', padding: '6px 0', borderBottom: '1px solid var(--border)' }}>
            <strong style={{ color: 'var(--text)' }}>{m.equipment_id}</strong> - {m.model} ({m.equipment_type})
          </li>
        ))}
        {widgetData.count > 3 && <li style={{ fontSize: '0.85rem', color: 'var(--accent)', marginTop: '8px', cursor: 'pointer' }}>+ {widgetData.count - 3} more...</li>}
      </ul>
    );
  };

  const handleAction = async (insight) => {
    if (!insight.action_label) return;
    
    // If it's an internal action, just alert and return
    if (!insight.action_label.startsWith("Notify")) {
      alert(`${insight.action_label} for ${insight.equipment_id} has been logged.`);
      return;
    }

    try {
      await notificationAPI.sendManual({
        recipient_id: insight.customer_user_id,
        title: insight.type === 'MAINTENANCE' ? 'Maintenance Scheduled' : 'Machine Alert',
        message: insight.message,
        priority: 'HIGH',
        notification_type: 'ALERT'
      });
      alert(`Notification successfully sent to ${insight.customer_name}!`);
    } catch (error) {
      console.error("Error sending notification", error);
      alert("Failed to send notification.");
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Dealer Dashboard</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Overview of fleet operations and revenue.</p>
      </div>

      {data.actionable_insights && data.actionable_insights.length > 0 && (
        <div style={{ marginBottom: '2.5rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', color: 'var(--text)' }}>Actionable Insights</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {data.actionable_insights.map(insight => (
              <div key={insight.id} style={{
                background: 'var(--surface)',
                border: '1px solid var(--border)',
                borderLeft: `4px solid ${insight.type === 'MAINTENANCE' ? 'var(--warning)' : insight.type === 'ANOMALY' ? 'var(--error)' : 'var(--primary)'}`,
                padding: '1.5rem',
                borderRadius: '12px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                boxShadow: '0 4px 6px rgba(0,0,0,0.02)'
              }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '5px' }}>
                    <span style={{ fontWeight: '700', color: 'var(--text)' }}>{insight.equipment_id}</span>
                    <span style={{ fontSize: '0.8rem', padding: '3px 8px', borderRadius: '12px', background: 'var(--background)', color: 'var(--text-secondary)' }}>
                      {insight.type.replace('_', ' ')}
                    </span>
                  </div>
                  <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{insight.message}</p>
                </div>
                {insight.action_label && (
                  <button 
                    onClick={() => handleAction(insight)}
                    style={{
                      background: 'var(--black)',
                      color: 'white',
                      border: 'none',
                      padding: '0.6rem 1.2rem',
                      borderRadius: '8px',
                      fontWeight: '600',
                      cursor: 'pointer',
                      transition: 'background 0.2s'
                    }}
                  >
                    {insight.action_label}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
        <Card title="Revenue This Month">
          <h2 style={{ fontSize: '2.5rem', margin: '10px 0', color: 'var(--primary)' }}>${data.revenue_this_month.toLocaleString()}</h2>
          <p style={{ color: 'var(--text-secondary)' }}>From {data.active_customers} active customers</p>
        </Card>

        <Card title="Total Inventory">
          <h2 style={{ fontSize: '2.5rem', margin: '10px 0', color: 'var(--text)' }}>{data.total_machines}</h2>
          <p style={{ color: 'var(--text-secondary)' }}>Owned machines</p>
        </Card>

        <Card title="Currently Rented">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--success)' }}>{data.rented_machines.count}</h2>
          {renderWidgetMachines(data.rented_machines)}
        </Card>

        <Card title="Available Machines">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--text)' }}>{data.available_machines.count}</h2>
          {renderWidgetMachines(data.available_machines)}
        </Card>

        <Card title="Under Maintenance">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--warning)' }}>{data.maintenance_machines.count}</h2>
          {renderWidgetMachines(data.maintenance_machines)}
        </Card>

        <Card title="Underutilized Alerts">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--error)' }}>{data.underutilized_machines.count}</h2>
          {renderWidgetMachines(data.underutilized_machines)}
        </Card>

        <Card title="Upcoming Returns (7 Days)">
          <h2 style={{ fontSize: '2rem', margin: '5px 0', color: 'var(--text)' }}>{data.upcoming_returns.count}</h2>
          {renderWidgetMachines(data.upcoming_returns)}
        </Card>
      </div>
    </div>
  );
};

export default DealerDashboard;
