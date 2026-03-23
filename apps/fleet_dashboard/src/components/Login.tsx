import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { yupResolver } from '@hookform/resolvers/yup';
import * as yup from 'yup';
import {
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Container
} from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

// Modern Design System - Professional Version
const designSystem = {
  colors: {
    primary: { 50: '#f8fafc', 100: '#f1f5f9', 500: '#3b82f6', 600: '#2563eb', 900: '#1e3a8a' },
    gray: { 50: '#ffffff', 100: '#f9fafb', 200: '#f3f4f6', 300: '#e5e7eb', 400: '#d1d5db', 500: '#9ca3af', 600: '#6b7280', 700: '#4b5563', 800: '#374151', 900: '#111827' },
    success: '#059669',
    warning: '#d97706',
    error: '#dc2626',
    info: '#0891b2'
  },
  typography: {
    xs: '0.75rem',
    sm: '0.875rem',
    base: '1rem',
    lg: '1.125rem',
    xl: '1.25rem',
    '2xl': '1.5rem',
    '3xl': '1.875rem',
    '4xl': '2.25rem'
  },
  spacing: {
    xs: '0.25rem',
    sm: '0.5rem',
    md: '0.75rem',
    lg: '1rem',
    xl: '1.5rem',
    '2xl': '2rem'
  },
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
  }
};

const schema = yup.object().shape({
  username: yup
    .string()
    .required('Username is required')
    .min(3, 'Username must be at least 3 characters')
    .max(30, 'Username must not exceed 30 characters'),
  password: yup
    .string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

interface LoginFormData {
  username: string;
  password: string;
}

export const Login: React.FC = () => {
  const { login, isLoading, error } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  const from = location.state?.from?.pathname || '/dashboard';

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormData>({
    resolver: yupResolver(schema),
  });

  const onSubmit = async (data: LoginFormData) => {
    await login(data.username, data.password);
    navigate(from, { replace: true });
  };

  return (
    <Container maxWidth="sm">
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          background: 'linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%)',
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
        }}
      >
        <Card 
          sx={{ 
            maxWidth: 400, 
            width: '100%', 
            mx: 2,
            borderRadius: '16px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
            border: '1px solid rgba(255, 255, 255, 0.8)',
            backdropFilter: 'blur(10px)',
            background: 'rgba(255, 255, 255, 0.95)'
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom 
              align="center"
              sx={{
                fontWeight: 700,
                color: '#111827',
                letterSpacing: '-0.025em',
                mb: 2
              }}
            >
              Fleet Control
            </Typography>
            <Typography 
              variant="body2" 
              color="text.secondary" 
              align="center" 
              sx={{ 
                mb: 3,
                color: '#6b7280',
                fontWeight: 500
              }}
            >
              Management Portal
            </Typography>

            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 2,
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  color: '#991b1b'
                }}
              >
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Username"
                {...register('username')}
                error={!!errors.username}
                helperText={errors.username?.message}
                margin="normal"
                required
                autoComplete="username"
                autoFocus
                disabled={isLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                    backgroundColor: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    '&:hover fieldset': {
                      borderColor: '#0ea5e9'
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#0ea5e9',
                      boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.1)'
                    }
                  }
                }}
              />
              <TextField
                fullWidth
                label="Password"
                type="password"
                {...register('password')}
                error={!!errors.password}
                helperText={errors.password?.message}
                margin="normal"
                required
                autoComplete="current-password"
                disabled={isLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                    backgroundColor: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    '&:hover fieldset': {
                      borderColor: '#0ea5e9'
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#0ea5e9',
                      boxShadow: '0 0 0 3px rgba(14, 165, 233, 0.1)'
                    }
                  }
                }}
              />
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{ 
                  mt: 3, 
                  mb: 2,
                  py: 1.5,
                  borderRadius: '8px',
                  background: '#3b82f6',
                  border: 'none',
                  fontWeight: 600,
                  fontSize: '1rem',
                  textTransform: 'none',
                  boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
                  '&:hover': {
                    background: '#2563eb',
                    transform: 'translateY(-1px)',
                    boxShadow: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
                  },
                  '&:active': {
                    transform: 'translateY(0)'
                  },
                  '&.Mui-disabled': {
                    background: '#e5e7eb',
                    color: '#9ca3af'
                  }
                }}
                disabled={isLoading}
                startIcon={isLoading && <CircularProgress size={20} />}
              >
                {isLoading ? 'Authenticating...' : 'Sign In'}
              </Button>
            </Box>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <Typography 
                variant="caption" 
                sx={{ 
                  color: '#6b7280',
                  fontSize: '0.875rem',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '0.5rem'
                }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path d="M12 15a3 3 0 100-6 3 3 0 000 6z" fill="currentColor" />
                  <path d="M12 1C6.48 1 2 5.59 2 11.17c0 2.76 1.12 5.26 2.93 7.08l.01.01c.39.39.78.72 1.18 1.01.63.44 1.29.81 1.98 1.1.91.38 1.87.58 2.85.63.05 0 .1.01.15.01.09 0 .18 0 .27-.01.98-.05 1.94-.25 2.85-.63.69-.29 1.35-.66 1.98-1.1.4-.29.79-.62 1.18-1.01l.01-.01c1.81-1.82 2.93-4.32 2.93-7.08C22 5.59 17.52 1 12 1zm0 20c-.09 0-.18 0-.27-.01-.89-.04-1.75-.23-2.56-.57-.58-.25-1.13-.57-1.64-.94-.36-.26-.71-.55-1.03-.87-1.57-1.57-2.54-3.74-2.54-6.15 0-4.96 4.04-9 9-9s9 4.04 9 9c0 2.41-.97 4.58-2.54 6.15-.32.32-.67.61-1.03.87-.51.37-1.06.69-1.64.94-.81.34-1.67.53-2.56.57-.09.01-.18.01-.27.01z" fill="currentColor" />
                </svg>
                Default credentials: <strong>admin / admin123</strong>
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};
