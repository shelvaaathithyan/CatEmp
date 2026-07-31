import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { rentalAPI, machineAPI } from '../../api';
import { toast } from 'react-toastify';

const CustomerRentalDetails = () => {
  const { rentalId } = useParams();
  const navigate = useNavigate();
  
  const [rental, setRental] = useState(null);
  const [machine, setMachine] = useState(null);
  const [timeline, setTimeline] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        // Fetch rental details
        const rentalData = await rentalAPI.getDetails(rentalId);
        setRental(rentalData);

        if (rentalData && rentalData.equipment_id) {
            // Fetch machine basic info
            const machineData = await machineAPI.getDetails(rentalData.equipment_id);
            setMachine(machineData);

            // Fetch timeline
            const timelineData = await machineAPI.getTimeline(rentalData.equipment_id);
            
            // Filter timeline for events that happened during this rental period
            const checkInDate = new Date(rentalData.check_in_date);
            const endDate = rentalData.actual_return_date ? new Date(rentalData.actual_return_date) : new Date();
            
            let filteredTimeline = (timelineData.timeline || []).filter(event => {
                const eventDate = new Date(event.timestamp);
                return eventDate >= checkInDate && eventDate <= endDate;
            });
            
            setTimeline([...filteredTimeline].reverse());
        }
      } catch (error) {
        console.error("Failed to fetch rental details:", error);
        toast.error("Failed to load rental details.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [rentalId]);

  const getEventIcon = (type) => {
    switch (type) {
      case 'RENTAL_CREATED': return '📝';
      case 'SITE_TRANSFER': return '🚚';
      case 'ACTION_CHECKIN': return '📥';
      case 'ACTION_CHECKOUT': return '📤';
      case 'MAINTENANCE': return '🔧';
      case 'USAGE': return '⏱️';
      default: return '📍';
    }
  };

  const getEventGradient = (type) => {
    switch (type) {
      case 'RENTAL_CREATED': return 'linear-gradient(135deg, #3b82f6, #2563eb)';
      case 'SITE_TRANSFER': return 'linear-gradient(135deg, #8b5cf6, #6d28d9)';
      case 'ACTION_CHECKIN': return 'linear-gradient(135deg, #10b981, #059669)';
      case 'ACTION_CHECKOUT': return 'linear-gradient(135deg, #f59e0b, #d97706)';
      case 'MAINTENANCE': return 'linear-gradient(135deg, #ef4444, #dc2626)';
      case 'USAGE': return 'linear-gradient(135deg, #0ea5e9, #0284c7)';
      default: return 'linear-gradient(135deg, #64748b, #475569)';
    }
  };

  const getStatusColor = (status) => {
    switch(status) {
      case 'ACTIVE': return '#10b981';
      case 'COMPLETED': return '#3b82f6';
      case 'PENDING': return '#f59e0b';
      default: return '#64748b';
    }
  };

  if (loading) {
    return <div style={{ color: 'var(--text)' }}>Loading rental details...</div>;
  }

  if (!rental) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-secondary)' }}>
        <h2>Rental not found</h2>
        <button onClick={() => navigate('/customer/rentals')} style={{
          padding: '0.75rem 1.5rem', background: 'var(--primary)', color: 'white',
          border: 'none', borderRadius: '8px', cursor: 'pointer', marginTop: '1rem'
        }}>
          Back to Rentals
        </button>
      </div>
    );
  }

  return (
    <div style={{ paddingBottom: '3rem' }}>
      {/* Header section */}
      <div style={{ display: 'flex', alignItems: 'center', marginBottom: '2rem', gap: '1rem' }}>
        <button 
          onClick={() => navigate('/customer/rentals')}
          style={{
            background: 'var(--surface)',
            border: '1px solid var(--border)',
            borderRadius: '50%',
            width: '40px', height: '40px',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            cursor: 'pointer',
            fontSize: '1.2rem',
            color: 'var(--text)'
          }}
          title="Back to Rentals"
        >
          ←
        </button>
        <div>
          <h1 style={{ fontSize: '2.5rem', marginBottom: '0.25rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>
            Rental #{rental.id}
          </h1>
          <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)', margin: 0 }}>
            {machine ? `${machine.equipment_type} • ${machine.model}` : rental.equipment_id}
          </p>
          <div style={{ marginTop: '0.5rem' }}>
              <span style={{ fontSize: '0.95rem', color: 'var(--text-secondary)' }}>Equipment ID: <strong style={{ color: 'var(--black)' }}>{rental.equipment_id}</strong></span>
          </div>
        </div>
        <div style={{ marginLeft: 'auto' }}>
           <div style={{ 
              display: 'inline-flex', alignItems: 'center', gap: '0.5rem', 
              padding: '0.5rem 1.25rem', borderRadius: '30px', 
              background: 'var(--surface)', border: '1px solid var(--border)',
              fontSize: '0.9rem', fontWeight: 'bold', color: 'var(--text)',
              boxShadow: '0 2px 10px rgba(0,0,0,0.05)'
            }}>
              <span style={{ width: '10px', height: '10px', borderRadius: '50%', background: getStatusColor(rental.rental_status) }}></span>
              {rental.rental_status}
            </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(200px, 1fr))', gap: '20px', marginBottom: '2rem' }}>
        <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '16px', boxShadow: 'var(--shadow-sm)' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Start Date</h3>
          <h2 style={{ fontSize: '1.5rem', margin: '0', color: 'var(--black)', fontWeight: '900' }}>{new Date(rental.check_in_date).toLocaleDateString()}</h2>
        </div>
        <div style={{ background: 'var(--surface)', padding: '1.5rem', borderRadius: '16px', boxShadow: 'var(--shadow-sm)' }}>
          <h3 style={{ fontSize: '0.85rem', color: 'var(--medium)', margin: '0 0 5px 0', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: '800' }}>Expected Return</h3>
          <h2 style={{ fontSize: '1.5rem', margin: '0', color: 'var(--black)', fontWeight: '900' }}>{new Date(rental.expected_return_date).toLocaleDateString()}</h2>
        </div>
      </div>

      {/* Main Timeline Card with Premium Styling */}
      <div style={{
        background: 'var(--surface)',
        borderRadius: '24px',
        border: '1px solid var(--border)',
        boxShadow: '0 10px 30px rgba(0,0,0,0.05)',
        overflow: 'hidden',
        maxWidth: '800px',
        margin: '0 auto'
      }}>
        <div style={{ 
          padding: '2rem 2.5rem', 
          background: 'var(--surface)',
          borderBottom: '1px solid var(--border)'
        }}>
          <h2 style={{ margin: 0, color: 'var(--text)', fontSize: '1.5rem', fontWeight: '700' }}>Rental Activity Timeline</h2>
          <p style={{ margin: '0.5rem 0 0 0', color: 'var(--text-secondary)' }}>A complete audit trail of this machine during your rental period.</p>
        </div>

        <div style={{ padding: '3rem', background: 'var(--background)' }}>
          {timeline.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '3rem 0', color: 'var(--text-secondary)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem', opacity: 0.5 }}>📭</div>
              <p>No historical events recorded during this rental period.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '2.5rem', position: 'relative' }}>
              {/* Vertical line connecting events */}
              <div style={{
                position: 'absolute',
                top: '24px', bottom: '24px',
                left: '27px',
                width: '2px',
                background: 'var(--border)',
                zIndex: 0
              }}></div>

              {timeline.map((event, index) => (
                <div key={index} className="timeline-event" style={{ 
                  display: 'flex', gap: '2rem', position: 'relative', zIndex: 1,
                  animation: `slideUp 0.5s ease-out ${index * 0.1}s forwards`,
                  opacity: 0,
                  transform: 'translateY(20px)'
                }}>
                  {/* Icon Node */}
                  <div style={{
                    width: '56px', height: '56px',
                    borderRadius: '50%',
                    background: getEventGradient(event.type),
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                    fontSize: '1.5rem',
                    color: '#fff',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.2)',
                    position: 'relative'
                  }}>
                    {getEventIcon(event.type)}
                    <div style={{ position: 'absolute', top: '-6px', left: '-6px', right: '-6px', bottom: '-6px', borderRadius: '50%', border: '1px solid var(--border)', zIndex: -1 }}></div>
                  </div>
                  
                  {/* Event Details Card */}
                  <div className="event-card" style={{
                    flex: 1,
                    background: 'var(--surface)',
                    padding: '1.5rem',
                    borderRadius: '16px',
                    border: '1px solid var(--border)',
                    boxShadow: '0 4px 15px rgba(0,0,0,0.05)',
                    transition: 'all 0.3s ease',
                    cursor: 'default'
                  }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
                      <span style={{ fontWeight: '700', color: 'var(--text)', fontSize: '1.1rem', letterSpacing: '0.5px' }}>
                        {event.type ? event.type.replace('_', ' ') : 'UNKNOWN'}
                      </span>
                      <span style={{ color: 'var(--text-secondary)', fontSize: '0.85rem', fontWeight: '600', padding: '0.3rem 0.8rem', background: 'var(--background)', borderRadius: '12px', border: '1px solid var(--border)' }}>
                        {new Date(event.timestamp).toLocaleString(undefined, { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '1rem', lineHeight: '1.6' }}>
                      {event.details}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes slideUp {
          from { opacity: 0; transform: translateY(20px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .event-card:hover {
          transform: translateY(-3px);
          background: var(--surface) !important;
          box-shadow: 0 10px 25px rgba(0,0,0,0.1) !important;
        }
      `}</style>
    </div>
  );
};

export default CustomerRentalDetails;
