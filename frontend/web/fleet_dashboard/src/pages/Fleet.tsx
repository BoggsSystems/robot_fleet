import React from 'react';
import Layout from '../components/Layout';

const Fleet: React.FC = () => {
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
          My Fleet
        </h1>
        <p style={{ 
          fontSize: '16px', 
          color: '#6b7280',
          lineHeight: 1.6
        }}>
          Fleet management page coming soon. This will display your robot fleet with real-time status, battery levels, and location information.
        </p>
      </div>
    </Layout>
  );
};

export default Fleet;
