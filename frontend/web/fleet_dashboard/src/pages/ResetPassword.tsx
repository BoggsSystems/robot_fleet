import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { authService } from '../services/api';

const ResetPassword: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [token, setToken] = useState<string>('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clientInfo, setClientInfo] = useState<any>(null);
  const [isResettingPassword, setIsResettingPassword] = useState(false);

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
      const response = await authService.validateResetToken(tokenValue);
      
      if (response.isValid) {
        setClientInfo({
          clientId: response.clientId,
          email: response.email,
          name: response.name
        });
      } else {
        setError('Invalid or expired reset link');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to validate reset token');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
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
      setIsResettingPassword(true);
      setError(null);
      
      const response = await authService.resetPassword(token, password);
      
      if (response.success) {
        // Redirect to login page with success message
        navigate('/login?message=' + encodeURIComponent('Password reset successfully! You can now login with your new password.'));
      } else {
        setError('Failed to reset password');
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to reset password');
    } finally {
      setIsResettingPassword(false);
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
            Validating reset link
          </h2>
          <div style={{ 
            fontSize: '14px', 
            color: '#6b7280', 
            marginBottom: '24px',
            lineHeight: 1.5
          }}>
            Please wait while we validate your password reset link...
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
            {error || 'This password reset link is invalid or has expired. Please request a new password reset.'}
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
        <div style={{ fontSize: '48px', marginBottom: '24px' }}>🔑</div>
        <h2 style={{ 
          fontSize: '24px', 
          fontWeight: 600, 
          color: '#1f2937', 
          marginBottom: '8px' 
        }}>
          Reset Your Password
        </h2>
        <p style={{ 
          fontSize: '14px', 
          color: '#6b7280', 
          marginBottom: '32px',
          lineHeight: 1.5
        }}>
          Hi <strong>{clientInfo.name}</strong>!<br />
          Enter your new password below.
        </p>
        
        <form onSubmit={handleResetPassword}>
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
              New Password *
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Enter your new password"
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
              disabled={isResettingPassword}
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
              Confirm New Password *
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirm your new password"
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
              disabled={isResettingPassword}
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
            disabled={isResettingPassword}
            style={{
              width: '100%',
              padding: '14px 24px',
              backgroundColor: isResettingPassword ? '#9ca3af' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              fontSize: '16px',
              fontWeight: 600,
              cursor: isResettingPassword ? 'not-allowed' : 'pointer',
              transition: 'all 0.2s ease'
            }}
          >
            {isResettingPassword ? 'Resetting Password...' : 'Reset Password'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default ResetPassword;
