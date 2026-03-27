import React, { useState } from 'react';
import { useNavigate, useLocation, Link as RouterLink } from 'react-router-dom';
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

const schema = yup.object().shape({
  email: yup
    .string()
    .required('Email is required')
    .email('Please enter a valid email'),
  password: yup
    .string()
    .required('Password is required')
    .min(6, 'Password must be at least 6 characters'),
});

interface LoginFormData {
  email: string;
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
    await login(data.email, data.password);
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
          background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
          fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
        }}
      >
        <Card 
          sx={{ 
            maxWidth: 400, 
            width: '100%', 
            mx: 2,
            borderRadius: '16px',
            boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.3), 0 10px 10px -5px rgba(0, 0, 0, 0.2)',
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            background: 'rgba(30, 41, 59, 0.95)'
          }}
        >
          <CardContent sx={{ p: 4 }}>
            <Box sx={{ textAlign: 'center', mb: 3 }}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 700,
                  color: '#60a5fa',
                  letterSpacing: '-0.025em'
                }}
              >
                Robot Fleet
              </Typography>
              <Typography
                variant="subtitle1"
                sx={{
                  color: '#94a3b8',
                  fontWeight: 500
                }}
              >
                Client Portal
              </Typography>
            </Box>

            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom 
              align="center"
              sx={{
                fontWeight: 700,
                color: '#f8fafc',
                letterSpacing: '-0.025em',
                mb: 2
              }}
            >
              Welcome Back
            </Typography>
            <Typography 
              variant="body2" 
              align="center" 
              sx={{ 
                mb: 3,
                color: '#94a3b8',
                fontWeight: 500
              }}
            >
              Sign in to manage your fleet
            </Typography>

            {error && (
              <Alert 
                severity="error" 
                sx={{ 
                  mb: 2,
                  borderRadius: '8px',
                  background: 'rgba(239, 68, 68, 0.1)',
                  border: '1px solid rgba(239, 68, 68, 0.2)',
                  color: '#fca5a5'
                }}
              >
                {error}
              </Alert>
            )}

            <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ mt: 2 }}>
              <TextField
                fullWidth
                label="Email"
                type="email"
                {...register('email')}
                error={!!errors.email}
                helperText={errors.email?.message}
                margin="normal"
                required
                autoComplete="email"
                autoFocus
                disabled={isLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                    backgroundColor: 'rgba(15, 23, 42, 0.5)',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    color: '#f8fafc',
                    '&:hover fieldset': {
                      borderColor: '#60a5fa'
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#60a5fa',
                      boxShadow: '0 0 0 3px rgba(96, 165, 250, 0.1)'
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: '#94a3b8'
                  },
                  '& .MuiFormHelperText-root': {
                    color: '#ef4444'
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
                    backgroundColor: 'rgba(15, 23, 42, 0.5)',
                    border: '1px solid rgba(148, 163, 184, 0.2)',
                    color: '#f8fafc',
                    '&:hover fieldset': {
                      borderColor: '#60a5fa'
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#60a5fa',
                      boxShadow: '0 0 0 3px rgba(96, 165, 250, 0.1)'
                    }
                  },
                  '& .MuiInputLabel-root': {
                    color: '#94a3b8'
                  },
                  '& .MuiFormHelperText-root': {
                    color: '#ef4444'
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
                    background: '#334155',
                    color: '#64748b'
                  }
                }}
                disabled={isLoading}
              >
                {isLoading ? <CircularProgress size={24} sx={{ color: 'white' }} /> : 'Sign In'}
              </Button>
            </Box>

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <RouterLink
                to="/forgot-password"
                style={{
                  color: '#60a5fa',
                  textDecoration: 'none',
                  fontSize: '14px'
                }}
              >
                Forgot password?
              </RouterLink>
            </Box>
          </CardContent>
        </Card>
      </Box>
    </Container>
  );
};
