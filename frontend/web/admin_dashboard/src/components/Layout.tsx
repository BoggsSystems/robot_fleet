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
    { path: '/', label: 'Dashboard', icon: '📊' },
    { path: '/clients', label: 'Clients', icon: '🏢' },
    { path: '/fleet', label: 'Global Fleet', icon: '🤖' },
    { path: '/users', label: 'Users', icon: '👥' },
    { path: '/system', label: 'System Health', icon: '🔧' },
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
            <p style={{ fontSize: '12px', color: '#94a3b8' }}>SuperAdmin</p>
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
              {user?.profile.firstName} {user?.profile.lastName}
            </p>
            <p style={{ fontSize: '12px', color: '#94a3b8' }}>{user?.role}</p>
          </div>
          <button
            onClick={logout}
            style={{
              width: '100%',
              padding: '8px 16px',
              backgroundColor: '#dc2626',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '14px',
              cursor: 'pointer'
            }}
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main style={{ flex: 1, overflow: 'auto' }}>
        {children}
      </main>
    </div>
  );
};

export default Layout;
