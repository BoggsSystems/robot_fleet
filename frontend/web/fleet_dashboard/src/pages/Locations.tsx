import React from 'react';
import Layout from '../components/Layout';

const Locations: React.FC = () => {
  return (
    <Layout>
      <div style={{
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
      }}>
        <h1 style={{ 
          fontSize: '32px', 
          fontWeight: 700,
          color: '#111827', 
          marginBottom: '24px',
          letterSpacing: '-0.025em'
        }}>
          Locations
        </h1>
        <p style={{ 
          fontSize: '16px', 
          color: '#6b7280',
          lineHeight: 1.6
        }}>
          Location management page coming soon. This will display your facility zones, robot positioning, and zone configuration.
        </p>
      </div>
    </Layout>
  );
};

export default Locations;
