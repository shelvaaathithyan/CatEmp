import Card from './Card';

const PlaceholderPage = ({ title, description }) => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)' }}>{title}</h1>
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)' }}>{description}</p>
      </div>
      <Card>
        <p style={{ color: 'var(--medium)', fontFamily: 'var(--font-body)' }}>This module is currently under development. Content for {title} will appear here.</p>
      </Card>
    </div>
  );
};

export default PlaceholderPage;
