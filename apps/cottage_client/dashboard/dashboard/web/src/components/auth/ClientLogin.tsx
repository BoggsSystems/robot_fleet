import { useState } from 'react';
import { Eye, EyeOff, Mail, Lock, Building2, ArrowRight } from 'lucide-react';
import './ClientLogin.css';

interface ClientLoginProps {
  onLogin: (credentials: { email: string; password: string }) => void;
  onSwitchToAdmin: () => void;
  isLoading?: boolean;
}

export function ClientLogin({ onLogin, onSwitchToAdmin, isLoading = false }: ClientLoginProps) {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    rememberMe: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setErrors({});

    // Basic validation
    const newErrors: Record<string, string> = {};
    if (!formData.email) newErrors.email = 'Email is required';
    if (!formData.password) newErrors.password = 'Password is required';
    if (formData.password.length < 6) newErrors.password = 'Password must be at least 6 characters';

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    onLogin(formData);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  return (
    <div className="client-login">
      <div className="login-container">
        <div className="login-header">
          <div className="client-logo">
            <Building2 size={32} />
          </div>
          <h1>Client Portal</h1>
          <p>Access your robot fleet dashboard</p>
        </div>

        <form className="login-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <div className="input-wrapper">
              <Mail size={18} className="input-icon" />
              <input
                id="email"
                name="email"
                type="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="your.email@company.com"
                className={errors.email ? 'error' : ''}
                disabled={isLoading}
              />
            </div>
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <div className="input-wrapper">
              <Lock size={18} className="input-icon" />
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                placeholder="Enter your password"
                className={errors.password ? 'error' : ''}
                disabled={isLoading}
              />
              <button
                type="button"
                className="password-toggle"
                onClick={() => setShowPassword(!showPassword)}
                disabled={isLoading}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <div className="form-options">
            <label className="checkbox-wrapper">
              <input
                name="rememberMe"
                type="checkbox"
                checked={formData.rememberMe}
                onChange={handleChange}
                disabled={isLoading}
              />
              <span>Remember me</span>
            </label>
            <button type="button" className="forgot-password" disabled={isLoading}>
              Forgot password?
            </button>
          </div>

          <button 
            type="submit" 
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <div className="spinner" />
                Signing in...
              </>
            ) : (
              <>
                Sign In to Client Portal
                <ArrowRight size={18} />
              </>
            )}
          </button>
        </form>

        <div className="login-footer">
          <div className="demo-accounts">
            <h4>Demo Accounts:</h4>
            <div className="demo-list">
              <div className="demo-item">
                <strong>TechCorp Industries:</strong>
                <code>s.mitchell@techcorp.com / demo123</code>
              </div>
              <div className="demo-item">
                <strong>Global Logistics:</strong>
                <code>m.chen@globallogistics.com / demo123</code>
              </div>
              <div className="demo-item">
                <strong>HealthFirst Medical:</strong>
                <code>e.rodriguez@healthfirst.com / demo123</code>
              </div>
            </div>
          </div>

          <div className="switch-mode">
            <span>Admin access?</span>
            <button 
              type="button" 
              className="switch-button"
              onClick={onSwitchToAdmin}
              disabled={isLoading}
            >
              Switch to Admin Login
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
