import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { dashboardAPI, notificationAPI } from '../../api';
import { PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const DealerDashboard = () => {
  const navigate = useNavigate();
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

  const handleAction = async (insight) => {
    if (!insight.action_label) return;
    
    if (!insight.action_label.startsWith("Notify")) {
      alert(`${insight.action_label} for ${insight.equipment_id} has been logged locally.`);
      return;
    }

    if (!insight.customer_user_id) {
        alert(`No customer found to send the notification to for ${insight.equipment_id}.`);
        return;
    }

    try {
      await notificationAPI.sendManual({
        recipient_id: insight.customer_user_id,
        title: `Action Required: ${insight.type}`,
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

  if (loading) return <div style={{ color: 'var(--text)' }}>Loading Dashboard...</div>;
  if (!data) return <div style={{ color: 'var(--error)' }}>Error loading Dashboard.</div>;

  const machineColumns = [
    { header: 'Equipment ID', accessor: 'equipment_id', cell: (row) => <span style={{ fontWeight: '700', color: 'var(--black)' }}>{row.equipment_id}</span> },
    { header: 'Model', accessor: 'model', cell: (row) => <span style={{ color: 'var(--medium)' }}>{row.model}</span> }
  ];

  return (
    <div style={{ paddingBottom: '2rem' }}>
      
      {/* 1. INTERACTIVE KPI CARDS AT TOP */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '20px', marginBottom: '2rem' }}>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9f9fa 100%)', border: '1px solid var(--border)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} onMouseOver={e=>e.currentTarget.style.transform='translateY(-4px)'} onMouseOut={e=>e.currentTarget.style.transform='translateY(0)'}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Total Fleet Size</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--black)', fontWeight: '900' }}>{data.total_machines}</h2>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9f9fa 100%)', border: '1px solid var(--border)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} onMouseOver={e=>e.currentTarget.style.transform='translateY(-4px)'} onMouseOut={e=>e.currentTarget.style.transform='translateY(0)'}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Active Rentals</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--success)', fontWeight: '900' }}>{data.rented_machines.count}</h2>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9f9fa 100%)', border: '1px solid var(--border)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} onMouseOver={e=>e.currentTarget.style.transform='translateY(-4px)'} onMouseOut={e=>e.currentTarget.style.transform='translateY(0)'}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Maintenance</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--error)', fontWeight: '900' }}>{data.maintenance_machines.count}</h2>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #fffde7 100%)', border: '1px solid var(--primary)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(241,196,15,0.15)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }} onMouseOver={e=>e.currentTarget.style.transform='translateY(-4px)'} onMouseOut={e=>e.currentTarget.style.transform='translateY(0)'}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Monthly Revenue</h3>
          <h2 style={{ fontSize: '2rem', margin: '0', color: 'var(--black)', fontWeight: '900' }}>${data.revenue_this_month.toLocaleString()}</h2>
        </div>
      </div>

      {/* 2. MIDDLE ROW: Actionable Insights (Left) & Fleet Distribution (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', marginBottom: '2rem' }}>
        
        {/* ACTIONABLE INSIGHTS */}
        {data.actionable_insights && data.actionable_insights.length > 0 ? (
          <div style={{ 
            background: 'var(--surface)', 
            borderRadius: '16px', 
            padding: '2rem',
            boxShadow: 'var(--shadow-md)',
            borderTop: '4px solid var(--primary)',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <h2 style={{ fontSize: '1.4rem', marginBottom: '1.5rem', fontFamily: 'var(--font-heading)', color: 'var(--black)' }}>Insights</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', overflowY: 'auto', maxHeight: '350px' }}>
              {data.actionable_insights.map(insight => (
                <div key={insight.id} style={{
                  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                  padding: '15px 20px', backgroundColor: 'var(--background)', borderRadius: '12px',
                  borderLeft: `4px solid ${insight.type === 'MAINTENANCE' ? 'var(--error)' : 'var(--primary)'}`
                }}>
                  <div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                      <span style={{ fontWeight: '800', color: 'var(--black)', fontSize: '1.1rem' }}>{insight.equipment_id}</span>
                      <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '4px', backgroundColor: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-secondary)', fontWeight: 'bold' }}>
                        {insight.type.replace('_', ' ')}
                      </span>
                    </div>
                    <p style={{ color: 'var(--medium)', margin: 0, fontSize: '0.95rem' }}>{insight.message}</p>
                  </div>
                  {insight.action_label && (
                    <button 
                      onClick={() => handleAction(insight)}
                      style={{
                        padding: '10px 20px', backgroundColor: 'var(--black)', color: 'white',
                        border: 'none', borderRadius: '8px', fontWeight: '700', cursor: 'pointer',
                        transition: 'all 0.2s',
                        boxShadow: '0 4px 10px rgba(0, 0, 0, 0.15)'
                      }}
                      onMouseOver={(e) => e.target.style.transform = 'translateY(-2px)'}
                      onMouseOut={(e) => e.target.style.transform = 'translateY(0)'}
                    >
                      {insight.action_label}
                    </button>
                  )}
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div style={{ background: 'var(--surface)', borderRadius: '16px', padding: '2rem', boxShadow: 'var(--shadow-sm)', borderTop: '4px solid var(--success)', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
             <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontWeight: '600' }}>No Insights Available.</p>
          </div>
        )}

        {/* DONUT CHART */}
        <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '16px', boxShadow: 'var(--shadow-sm)' }}>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--black)', marginBottom: '1rem' }}>Fleet Distribution</h3>
          <div style={{ height: '250px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie 
                  data={data.fleet_status_chart} 
                  innerRadius={70} 
                  outerRadius={100} 
                  paddingAngle={5} 
                  dataKey="value"
                >
                  {data.fleet_status_chart.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          {/* Custom Legend */}
          <div style={{ display: 'flex', justifyContent: 'center', gap: '15px', marginTop: '10px' }}>
            {data.fleet_status_chart.map((entry, index) => (
              <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: entry.fill }} />
                <span style={{ fontSize: '0.85rem', color: 'var(--medium)', fontWeight: '600' }}>{entry.name}</span>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* 3. REVENUE TREND CHART (Full Width) */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '16px', boxShadow: 'var(--shadow-sm)' }}>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--black)', marginBottom: '1rem' }}>6-Month Revenue Trend</h3>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.revenue_trend_chart} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="month" stroke="var(--medium)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--medium)" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `$${val / 1000}k`} />
                <Tooltip formatter={(value) => `$${value.toLocaleString()}`} />
                <Area type="monotone" dataKey="revenue" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorRev)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. LOGISTICS FEED */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
        <Card title="Upcoming Returns (7 Days)">
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '15px' }}>
            <h2 style={{ fontSize: '2.5rem', margin: '0', color: 'var(--warning)', fontWeight: '900' }}>{data.upcoming_returns.count}</h2>
            <span style={{ color: 'var(--medium)', fontWeight: '700', fontSize: '0.9rem', textTransform: 'uppercase' }}>Machines</span>
          </div>
          {data.upcoming_returns.machines && data.upcoming_returns.machines.length > 0 ? (
            <Table 
              columns={machineColumns} 
              data={data.upcoming_returns.machines.slice(0, 5)} 
              onRowClick={(machine) => navigate(`/dealer/machines/${machine.equipment_id}`)}
            />
          ) : (
            <p style={{ color: 'var(--medium)' }}>None</p>
          )}
        </Card>
        
        <Card title="Underutilized Machines (Cost Saving)">
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '10px', marginBottom: '15px' }}>
            <h2 style={{ fontSize: '2.5rem', margin: '0', color: 'var(--primary)', fontWeight: '900' }}>{data.underutilized_machines.count}</h2>
            <span style={{ color: 'var(--medium)', fontWeight: '700', fontSize: '0.9rem', textTransform: 'uppercase' }}>Machines</span>
          </div>
          {data.underutilized_machines.machines && data.underutilized_machines.machines.length > 0 ? (
            <Table 
              columns={machineColumns} 
              data={data.underutilized_machines.machines.slice(0, 5)} 
              onRowClick={(machine) => navigate(`/dealer/machines/${machine.equipment_id}`)}
            />
          ) : (
            <p style={{ color: 'var(--medium)' }}>None</p>
          )}
        </Card>
      </div>
      
    </div>
  );
};

export default DealerDashboard;
