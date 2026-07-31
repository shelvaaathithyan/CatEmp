import { useState, useEffect } from 'react';
import Card from '../../components/common/Card';
import { dashboardAPI, notificationAPI } from '../../api';

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
    if (!widgetData || !widgetData.machines || widgetData.machines.length === 0) return <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>No machines</p>;
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

  const handleAction = async (insight) => {
    if (!insight.action_label) return;
    
    // If it's an internal action (like Initiate Return) that isn't an alert
    if (!insight.action_label.startsWith("Alert") && !insight.action_label.startsWith("Acknowledge")) {
      alert(`${insight.action_label} for ${insight.equipment_id} has been logged.`);
      return;
    }

    if (!insight.target_user_id) {
        alert(`No target user (Site Manager) found to send the notification to for ${insight.equipment_id}.`);
        return;
    }

    try {
      await notificationAPI.sendManual({
        recipient_id: insight.target_user_id,
        title: `Dashboard Alert: ${insight.type}`,
        message: insight.message,
        priority: insight.type === 'OVERUTILIZATION' ? 'HIGH' : 'INFO',
        notification_type: 'ALERT'
      });
      alert(`Notification successfully sent to site manager!`);
    } catch (error) {
      console.error("Error sending notification", error);
      alert("Failed to send notification.");
    }
  };

  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>Customer Dashboard</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>Overview of your rented machines and sites.</p>
      </div>

      {/* Actionable Insights */}
      {data.actionable_insights && data.actionable_insights.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', fontFamily: 'var(--font-heading)', color: 'var(--black)' }}>Actionable Insights</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            {data.actionable_insights.map(insight => (
              <div key={insight.id} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '20px', backgroundColor: 'var(--surface)', borderRadius: '12px',
                borderLeft: `4px solid ${insight.type === 'OVERUTILIZATION' ? 'var(--error)' : insight.type === 'IDLE_EQUIPMENT' ? 'var(--warning)' : 'var(--primary)'}`,
                boxShadow: 'var(--shadow-sm)'
              }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                    <span style={{ fontWeight: '700', color: 'var(--text)' }}>{insight.equipment_id}</span>
                    <span style={{ fontSize: '0.8rem', padding: '2px 8px', borderRadius: '4px', backgroundColor: 'var(--background)', color: 'var(--text-secondary)' }}>
                      {insight.type.replace('_', ' ')}
                    </span>
                  </div>
                  <p style={{ color: 'var(--text-secondary)', margin: 0 }}>{insight.message}</p>
                </div>
                {insight.action_label && (
                  <button 
                    onClick={() => handleAction(insight)}
                    style={{
                      padding: '10px 20px', backgroundColor: 'var(--black)', color: 'white',
                      border: 'none', borderRadius: '8px', fontWeight: '600', cursor: 'pointer',
                      transition: 'background-color 0.2s'
                    }}
                    onMouseOver={(e) => e.target.style.backgroundColor = 'var(--medium)'}
                    onMouseOut={(e) => e.target.style.backgroundColor = 'var(--black)'}
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
