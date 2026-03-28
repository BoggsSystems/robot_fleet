import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';
import { useAuth } from '../contexts/AuthContext';

const SetupPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [token, setToken] = useState<string>('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientInfo, setClientInfo] = useState<any>(null);
  const [isSettingPassword, setIsSettingPassword] = useState(false);
  const [showSuccessModal, setShowSuccessModal] = useState(false);
  const [passwordSetSuccess, setPasswordSetSuccess] = useState(false);

  useEffect(() => {
    const tokenFromUrl = searchParams.get('token');
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
      validateToken(tokenFromUrl);
    }
  }, [searchParams]);

  const validateToken = async (tokenValue: string) => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Add timeout to prevent infinite loading
      const timeoutPromise = new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Request timeout')), 10000);
      });
      
      const response = await Promise.race([
        authService.validateMagicToken(tokenValue),
        timeoutPromise
      ]);
      
      if (response.isValid) {
        setClientInfo({
          clientId: response.clientId,
          email: response.email,
          name: response.name
        });
      } else {
        setError('Invalid or expired magic link');
      }
    } catch (err: any) {
      console.error('Token validation error:', err);
      setError(err.response?.data?.error || err.message || 'Failed to validate token');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (password.length < 8) {
      setError('Password must be at least 8 characters long');
      return;
    }
    
    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    try {
      setIsSettingPassword(true);
      setError(null);
      
      console.log('🔍 DEBUG: Setting password with token:', token);
      const response = await authService.setPassword(token, password);
      console.log('🔍 DEBUG: Set password response:', response);
      
      if (response.success) {
        console.log('🔍 DEBUG: Password set successfully, client info:', response);
        setPasswordSetSuccess(true);
        setShowSuccessModal(true);
      } else {
        console.log('🔍 DEBUG: Password set failed:', response);
        setError('Failed to set password');
      }
    } catch (err: any) {
      console.log('🔍 DEBUG: Set password error:', err);
      setError(err.response?.data?.error || 'Failed to set password');
    } finally {
      setIsSettingPassword(false);
    }
  };

  const handleSuccessModalConfirm = async () => {
    console.log('🔍 DEBUG: User confirmed success modal, attempting login...');
    
    try {
      // Auto-login the user after successful password setup
      console.log('🔍 DEBUG: Attempting login with email:', clientInfo?.email);
      await login(clientInfo.email, password);
      console.log('🔍 DEBUG: Login successful, redirecting to dashboard...');
      
      // Redirect directly to dashboard after successful login
      navigate('/dashboard');
    } catch (loginErr: any) {
      console.log('🔍 DEBUG: Login failed:', loginErr);
      console.log('🔍 DEBUG: Login error details:', loginErr.response?.data);
      
      // Fallback to login if auto-login fails
      console.log('🔍 DEBUG: Falling back to login page...');
      navigate('/login?message=' + encodeURIComponent('Password set successfully! Please login to continue.'));
    }
  };

  if (isLoading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
      }}>
        <div style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          maxWidth: '400px',
          width: '100%'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '24px' }}>🔐</div>
          <h2 style={{ 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#1f2937', 
            marginBottom: '16px' 
          }}>
            Setting up your account
          </h2>
          <div style={{ 
            fontSize: '14px', 
            color: '#6b7280', 
            marginBottom: '24px',
            lineHeight: 1.5
          }}>
            Validating your magic link...
          </div>
        </div>
      </div>
    );
  }

  if (!clientInfo) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        minHeight: '100vh',
        backgroundColor: '#f8fafc',
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
      }}>
        <div style={{
          padding: '40px',
          textAlign: 'center',
          backgroundColor: 'white',
          borderRadius: '12px',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
          maxWidth: '400px',
          width: '100%'
        }}>
          <div style={{ fontSize: '48px', marginBottom: '24px' }}>⚠️</div>
          <h2 style={{ 
            fontSize: '24px', 
            fontWeight: 600, 
            color: '#dc2626', 
            marginBottom: '16px' 
          }}>
            Invalid or Expired Link
          </h2>
          <p style={{ 
            fontSize: '14px', 
            color: '#6b7280', 
            marginBottom: '24px',
            lineHeight: 1.5
          }}>
            {error || 'This magic link is invalid or has expired. Please contact your administrator.'}
          </p>
          <button
            onClick={() => navigate('/login')}
            style={{
              padding: '12px 24px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '14px',
              fontWeight: 500,
              cursor: 'pointer'
            }}
          >
            Return to Login
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ 
      display: 'flex', 
      justifyContent: 'center', 
      alignItems: 'center', 
      minHeight: '100vh',
      backgroundColor: '#f8fafc',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    }}>
      <div style={{
        padding: '40px',
        textAlign: 'center',
        backgroundColor: 'white',
        borderRadius: '12px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        maxWidth: '400px',
        width: '100%'
      }}>
        <div style={{ fontSize: '48px', marginBottom: '24px' }}>🤖</div>
        <h2 style={{ 
          fontSize: '24px', 
          fontWeight: 600, 
          color: '#1f2937', 
          marginBottom: '8px' 
        }}>
          Welcome to Robot Fleet
        </h2>
        <p style={{ 
          fontSize: '14px', 
          color: '#6b7280', 
          marginBottom: '32px',
          lineHeight: 1.5
        }}>
          Hi <strong>{clientInfo.name}</strong>!<br />
          You've been invited to set up your account password.
        </p>
        
        <form onSubmit={handleSetPassword}>
          <div style={{ marginBottom: '24px' }}>
            <label style={{ 
              display: 'block', 
              fontSize: '14px', 
              fontWeight: 500, 
              color: '#374151', 
              marginBottom: '8px' 
            }}>
              Email
            </label>
            <div style={{
              padding: '12px 16px',
              backgroundColor: '#f3f4f6',
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              color: '#6b7280',
              fontSize: '14px'
            }}>
              {clientInfo.email}
            </div>
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ 
              display: 'block', 
              fontSize: '14px', 
              fontWeight: 500, 
              color: '#374151', 
              marginBottom: '8px' 
            }}>
              Password *
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your password"
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: '#f9fafb',
                border: error ? '1px solid #dc2626' : '1px solid #e5e7eb',
                borderRadius: '8px',
                color: '#111827',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              disabled={isSettingPassword}
            />
          </div>

          <div style={{ marginBottom: '24px' }}>
            <label style={{ 
              display: 'block', 
              fontSize: '14px', 
              fontWeight: 500, 
              color: '#374151', 
              marginBottom: '8px' 
            }}>
              Confirm Password *
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your password"
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: '#f9fafb',
                border: error ? '1px solid #dc2626' : '1px solid #e5e7eb',
                borderRadius: '8px',
                color: '#111827',
                fontSize: '14px',
                outline: 'none',
                boxSizing: 'border-box'
              }}
              disabled={isSettingPassword}
            />
          </div>

          {error && (
            <div style={{
              padding: '12px 16px',
              backgroundColor: '#fef2f2',
              border: '1px solid #fecaca',
              borderRadius: '8px',
              color: '#dc2626',
              fontSize: '14px',
              marginBottom: '24px'
            }}>
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={isSettingPassword}
            style={{
              width: '100%',
              padding: '14px 24px',
              backgroundColor: isSettingPassword ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: isSettingPassword ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {isSettingPassword ? 'Setting Password...' : 'Set Password'}
          </button>
        </form>
      </div>

      {/* Success Modal */}
      {showSuccessModal && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          backgroundColor: 'rgba(0, 0, 0, 0.5)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 1000
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '32px',
            maxWidth: '400px',
            width: '90%',
            textAlign: 'center',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
          }}>
            <div style={{
              width: '64px',
              height: '64px',
              backgroundColor: '#10b981',
              borderRadius: '50%',
              display: 'flex',
              justifyContent: 'center',
              alignItems: 'center',
              margin: '0 auto 24px'
            }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"></polyline>
              </svg>
            </div>
            
            <h2 style={{
              fontSize: '24px',
              fontWeight: 700,
              color: '#111827',
              marginBottom: '12px',
              margin: '0 0 12px 0'
            }}>
              Password Set Successfully!
            </h2>
            
            <p style={{
              fontSize: '16px',
              color: '#6b7280',
              lineHeight: '1.5',
              marginBottom: '32px',
              margin: '0 0 32px 0'
            }}>
              Your password has been set successfully. You'll now be taken to your dashboard where you can start managing your robot fleet.
            </p>
            
            <button
              onClick={handleSuccessModalConfirm}
              style={{
                width: '100%',
                padding: '14px 24px',
                backgroundColor: '#3b82f6',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 600,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Take Me to Dashboard
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SetupPassword;
