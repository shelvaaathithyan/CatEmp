import React from 'react';

const PageHeader = ({ title, description, primaryAction }) => {
  return (
    <div style={{ marginBottom: '2rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
        <h1 style={{ fontSize: '2.5rem', fontFamily: 'var(--font-heading)', fontWeight: '800', color: 'var(--black)', margin: 0 }}>
          {title}
        </h1>
        {primaryAction && (
          <div>
            {primaryAction}
          </div>
        )}
      </div>
      {description && (
        <p style={{ color: 'var(--medium)', fontSize: '1.1rem', fontFamily: 'var(--font-body)', margin: 0 }}>
          {description}
        </p>
      )}
    </div>
  );
};

export default PageHeader;
