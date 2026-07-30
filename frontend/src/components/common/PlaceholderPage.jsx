import Card from './Card';

const PlaceholderPage = ({ title, description }) => {
  return (
    <div>
      <div style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem', fontFamily: 'Manrope, sans-serif', color: 'var(--text)' }}>{title}</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '1.1rem' }}>{description}</p>
      </div>
      <Card>
        <p style={{ color: 'var(--text-secondary)' }}>This module is currently under development. Content for {title} will appear here.</p>
      </Card>
    </div>
  );
};

export default PlaceholderPage;
