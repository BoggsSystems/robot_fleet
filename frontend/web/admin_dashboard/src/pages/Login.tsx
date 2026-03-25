import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';

const Login: React.FC = () => {
  const { login, isLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!username || !password) {
      setError('Please enter both username and password');
      return;
    }

    try {
      await login(username, password);
    } catch (err) {
      setError('Invalid credentials');
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: '#0f172a',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        backgroundColor: '#1e293b',
        borderRadius: '12px',
        padding: '40px',
        border: '1px solid #334155'
      }}>
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🤖</div>
          <h1 style={{ 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#f8fafc',
            marginBottom: '8px'
          }}>
            Robot Fleet
          </h1>
          <p style={{ fontSize: '14px', color: '#94a3b8' }}>
            SuperAdmin Portal
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit}>
          {error && (
            <div style={{
              backgroundColor: '#dc262620',
              border: '1px solid #dc2626',
              color: '#dc2626',
              padding: '12px',
              borderRadius: '6px',
              marginBottom: '16px',
              fontSize: '14px'
            }}>
              {error}
            </div>
          )}

          <div style={{ marginBottom: '16px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#e2e8f0',
              marginBottom: '6px'
            }}>
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#0f172a',
                border: '1px solid #475569',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: '14px',
                outline: 'none'
              }}
              placeholder="Enter username"
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{
              display: 'block',
              fontSize: '14px',
              fontWeight: 500,
              color: '#e2e8f0',
              marginBottom: '6px'
            }}>
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: '#0f172a',
                border: '1px solid #475569',
                borderRadius: '6px',
                color: '#f8fafc',
                fontSize: '14px',
                outline: 'none'
              }}
              placeholder="Enter password"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              fontSize: '16px',
              fontWeight: 500,
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.7 : 1
            }}
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        {/* Demo Note */}
        <p style={{
          marginTop: '24px',
          fontSize: '12px',
          color: '#64748b',
          textAlign: 'center'
        }}>
          Demo: Use any username/password for Phase 1 testing
        </p>
      </div>
    </div>
  );
};

export default Login;
