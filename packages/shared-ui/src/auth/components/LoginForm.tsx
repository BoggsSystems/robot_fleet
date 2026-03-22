import React, { useState } from 'react';
import { LoginRequest } from '../types/auth';
import { AuthService } from '../services/authService';

interface LoginFormProps {
  onLogin: (user: any) => void;
  onError: (error: string) => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onLogin, onError }) => {
  const [credentials, setCredentials] = useState<LoginRequest>({
    email: '',
    password: '',
  });
  const [loading, setLoading] = useState(false);

  const authService = new AuthService();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    onError('');

    try {
      const authResponse = await authService.login(credentials);
      onLogin(authResponse.user);
    } catch (error: any) {
      onError(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setCredentials({
      ...credentials,
      [e.target.name]: e.target.value,
    });
  };

  return (
    <div className="login-form">
      <h2>Robot Fleet Management</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email">Email</label>
          <input
            type="email"
            id="email"
            name="email"
            value={credentials.email}
            onChange={handleChange}
            required
            disabled={loading}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            value={credentials.password}
            onChange={handleChange}
            required
            disabled={loading}
          />
        </div>

        {loading && (
          <div className="loading">
            Authenticating...
          </div>
        )}

        <button type="submit" disabled={loading}>
          {loading ? 'Signing In...' : 'Sign In'}
        </button>
      </form>

      <div className="demo-accounts">
        <h3>Demo Accounts</h3>
        <div className="demo-account">
          <strong>Super Admin:</strong> admin@robotfleet.com / demo123
        </div>
        <div className="demo-account">
          <strong>Client Admin:</strong> client1@abc.com / demo123
        </div>
        <div className="demo-account">
          <strong>Operator:</strong> operator1@abc.com / demo123
        </div>
      </div>
    </div>
  );
};
