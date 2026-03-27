import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { user, logout } = useAuth();
  const location = useLocation();

  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: '📊' },
    { path: '/fleet', label: 'My Fleet', icon: '🤖' },
    { path: '/locations', label: 'Locations', icon: '📍' },
    { path: '/analytics', label: 'Analytics', icon: '📈' },
    { path: '/settings', label: 'Settings', icon: '⚙️' },
  ];

  return (
    <div style={{ display: 'flex', height: '100vh', backgroundColor: '#0f172a' }}>
      {/* Sidebar */}
      <aside style={{
        width: '250px',
        backgroundColor: '#1e293b',
        borderRight: '1px solid #334155',
        display: 'flex',
        flexDirection: 'column'
      }}>
        {/* Logo */}
        <div style={{
          padding: '20px',
          borderBottom: '1px solid #334155',
          display: 'flex',
          alignItems: 'center',
          gap: '10px'
        }}>
          <span style={{ fontSize: '24px' }}>🤖</span>
          <div>
            <h1 style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>
              Robot Fleet
            </h1>
            <p style={{ fontSize: '12px', color: '#94a3b8' }}>Client Portal</p>
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ flex: 1, padding: '16px' }}>
          {navItems.map(item => (
            <Link
              key={item.path}
              to={item.path}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                padding: '12px 16px',
                marginBottom: '4px',
                borderRadius: '8px',
                textDecoration: 'none',
                color: location.pathname === item.path ? '#f8fafc' : '#94a3b8',
                backgroundColor: location.pathname === item.path ? '#3b82f6' : 'transparent',
                transition: 'all 0.2s'
              }}
            >
              <span>{item.icon}</span>
              <span style={{ fontSize: '14px', fontWeight: 500 }}>{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* User Section */}
        <div style={{
          padding: '16px',
          borderTop: '1px solid #334155'
        }}>
          <div style={{ marginBottom: '12px' }}>
            <p style={{ fontSize: '14px', fontWeight: 500, color: '#f8fafc' }}>
              {user?.profile?.firstName || 'User'}
            </p>
            <p style={{ fontSize: '12px', color: '#94a3b8' }}>
              {user?.role || 'Client'}
            </p>
          </div>
          <button
            onClick={logout}
            style={{
              width: '100%',
              padding: '8px 16px',
              backgroundColor: 'transparent',
              border: '1px solid #475569',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer',
              color: '#94a3b8',
              transition: 'all 0.2s'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = '#334155';
              e.currentTarget.style.color = '#f8fafc';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = '#94a3b8';
            }}
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ 
        flex: 1, 
        overflow: 'auto', 
        padding: '0',
        display: 'flex',
        flexDirection: 'column'
      }}>
        <div style={{ 
          flex: 1,
          padding: '24px',
          background: '#f8fafc',
          minHeight: '100%'
        }}>
          {children}
        </div>
      </main>
    </div>
  );
};

export default Layout;
