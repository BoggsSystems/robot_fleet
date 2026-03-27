import React from 'react';
import Layout from '../components/Layout';

const Analytics: React.FC = () => {
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
          Analytics
        </h1>
        <p style={{ 
          fontSize: '16px', 
          color: '#6b7280',
          lineHeight: 1.6
        }}>
          Analytics dashboard coming soon. This will display usage statistics, robot performance metrics, and operational insights for your fleet.
        </p>
      </div>
    </Layout>
  );
};

export default Analytics;
