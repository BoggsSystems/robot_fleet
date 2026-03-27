import React from 'react';
import Layout from '../components/Layout';

const Settings: React.FC = () => {
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
          Settings
        </h1>
        <p style={{ 
          fontSize: '16px', 
          color: '#6b7280',
          lineHeight: 1.6
        }}>
          Account settings page coming soon. This will allow you to manage your profile, notification preferences, and security settings.
        </p>
      </div>
    </Layout>
  );
};

export default Settings;
