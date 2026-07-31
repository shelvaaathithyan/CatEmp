import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Card from '../../components/common/Card';
import Table from '../../components/common/Table';
import { dashboardAPI, notificationAPI } from '../../api';
import { PieChart, Pie, Cell, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const FleetDashboard = () => {
  const navigate = useNavigate();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await dashboardAPI.getFleetManagerDashboard();
        setData(result);
      } catch (error) {
        console.error("Error fetching fleet dashboard", error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleAction = async (insight) => {
    if (!insight.action_label) return;
    
    // Internal Action Handling
    if (insight.action_label === "Schedule Site Transfer") {
      alert(`Transfer flow initiated for ${insight.equipment_id}.`);
      return;
    } else if (insight.action_label === "Stop Machine") {
      alert(`Stop command sent for ${insight.equipment_id}.`);
      return;
    } else {
      alert(`Action logged: ${insight.action_label}`);
      return;
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
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9f9fa 100%)', border: '1px solid var(--border)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Active Machines</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--success)', fontWeight: '900' }}>{data.active_machines.count}</h2>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9f9fa 100%)', border: '1px solid var(--border)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Today's Check-ins</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--black)', fontWeight: '900' }}>{data.today_checkins}</h2>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #f9f9fa 100%)', border: '1px solid var(--border)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(0,0,0,0.05)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Today's Check-outs</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--black)', fontWeight: '900' }}>{data.today_checkouts}</h2>
        </div>
        <div style={{ background: 'linear-gradient(135deg, #ffffff 0%, #fffde7 100%)', border: '1px solid var(--primary)', padding: '1.2rem', borderRadius: '16px', boxShadow: '0 4px 15px rgba(241,196,15,0.15)', transition: 'transform 0.2s', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Pending Transfers</h3>
          <h2 style={{ fontSize: '2.2rem', margin: '0', color: 'var(--warning)', fontWeight: '900' }}>{data.pending_transfers}</h2>
        </div>
      </div>

      {/* 2. MIDDLE ROW: Actionable Insights & Predictions (Left) & Machine Status (Right) */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.5fr 1fr', gap: '20px', marginBottom: '2rem' }}>
        
        {/* ACTIONABLE INSIGHTS & PREDICTIONS */}
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
                borderLeft: `4px solid ${insight.type === 'OVERUTILIZATION' ? 'var(--error)' : insight.type === 'IDLE_EQUIPMENT' ? 'var(--warning)' : 'var(--primary)'}`
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
                  >
                    {insight.action_label}
                  </button>
                )}
              </div>
            ))}
            
            {/* Predictions Block */}
            {data.prediction_insights && data.prediction_insights.length > 0 && data.prediction_insights.map((pred, idx) => (
              <div key={`pred-${idx}`} style={{
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                padding: '15px 20px', backgroundColor: 'var(--background)', borderRadius: '12px',
                borderLeft: `4px solid #8b5cf6` // Purple for predictions
              }}>
                <div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '4px' }}>
                    <span style={{ fontWeight: '800', color: 'var(--black)', fontSize: '1.1rem' }}>Demand Alert</span>
                    <span style={{ fontSize: '0.75rem', padding: '2px 8px', borderRadius: '4px', backgroundColor: 'var(--surface)', border: '1px solid var(--border)', color: 'var(--text-secondary)', fontWeight: 'bold' }}>
                      AI PREDICTION
                    </span>
                  </div>
                  <p style={{ color: 'var(--medium)', margin: 0, fontSize: '0.95rem' }}>
                    Predicted demand for <strong>{pred.equipment_type}</strong> in {pred.period}: <strong>{pred.expected_demand} units</strong>.
                  </p>
                </div>
              </div>
            ))}

            {data.actionable_insights.length === 0 && data.prediction_insights.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--medium)', padding: '2rem 0' }}>
                No insights available.
              </div>
            )}
          </div>
        </div>

        {/* DONUT CHART */}
        <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '16px', boxShadow: 'var(--shadow-sm)' }}>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--black)', marginBottom: '1rem' }}>Machine Status Distribution</h3>
          <div style={{ height: '250px' }}>
            {data.machine_status_chart && data.machine_status_chart.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie 
                    data={data.machine_status_chart} 
                    innerRadius={70} 
                    outerRadius={100} 
                    paddingAngle={5} 
                    dataKey="value"
                  >
                    {data.machine_status_chart.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.fill} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'flex', height: '100%', alignItems: 'center', justifyContent: 'center', color: 'var(--medium)' }}>
                No machines at this site.
              </div>
            )}
          </div>
          {/* Custom Legend */}
          {data.machine_status_chart && (
            <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '15px', marginTop: '10px' }}>
              {data.machine_status_chart.map((entry, index) => (
                <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
                  <div style={{ width: '12px', height: '12px', borderRadius: '50%', backgroundColor: entry.fill }} />
                  <span style={{ fontSize: '0.85rem', color: 'var(--medium)', fontWeight: '600' }}>{entry.name} ({entry.value})</span>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* 3. COST TREND CHART (Full Width) */}
      <div style={{ marginBottom: '2rem' }}>
        <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '16px', boxShadow: 'var(--shadow-sm)' }}>
          <h3 style={{ fontSize: '1.2rem', color: 'var(--black)', marginBottom: '1rem' }}>7-Day Usage Trend (Total Engine Hours)</h3>
          <div style={{ height: '280px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data.usage_trend_chart} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorUsage" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3498db" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#3498db" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="date" stroke="var(--medium)" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="var(--medium)" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip />
                <Area type="monotone" dataKey="hours" stroke="#3498db" strokeWidth={3} fillOpacity={1} fill="url(#colorUsage)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 4. LOGISTICS FEED */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
        <Card title="Active Machines List">
          {data.active_machines.machines && data.active_machines.machines.length > 0 ? (
            <Table 
              columns={machineColumns} 
              data={data.active_machines.machines} 
              onRowClick={() => navigate(`/fleet/site`)}
            />
          ) : (
            <p style={{ color: 'var(--medium)' }}>No active machines.</p>
          )}
        </Card>
      </div>
      
    </div>
  );
};

export default FleetDashboard;
