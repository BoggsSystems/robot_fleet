import { AuthResponse, LoginRequest, RegisterRequest, User, Permission, UserRole } from '../types/auth';

export class AuthService {
  private baseUrl: string;
  private token: string | null = null;

  constructor() {
    this.baseUrl = (typeof window !== 'undefined' && (window as any).REACT_APP_API_URL) || 'http://localhost:8001';
    this.token = localStorage.getItem('auth_token');
  }

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Login failed');
    }

    const authData: AuthResponse = await response.json();
    this.token = authData.token;
    localStorage.setItem('auth_token', authData.token);
    localStorage.setItem('user_data', JSON.stringify(authData.user));
    
    return authData;
  }

  async register(userData: RegisterRequest): Promise<AuthResponse> {
    const response = await fetch(`${this.baseUrl}/api/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    const authData: AuthResponse = await response.json();
    this.token = authData.token;
    localStorage.setItem('auth_token', authData.token);
    localStorage.setItem('user_data', JSON.stringify(authData.user));
    
    return authData;
  }

  async getCurrentUser(): Promise<User | null> {
    if (!this.token) {
      return null;
    }

    try {
      const response = await fetch(`${this.baseUrl}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to get current user');
      }

      const user: User = await response.json();
      localStorage.setItem('user_data', JSON.stringify(user));
      return user;
    } catch (error) {
      this.logout();
      return null;
    }
  }

  async logout(): Promise<void> {
    if (this.token) {
      try {
        await fetch(`${this.baseUrl}/api/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.token}`,
          },
        });
      } catch (error) {
        console.error('Logout error:', error);
      }
    }

    this.token = null;
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user_data');
  }

  async refreshToken(): Promise<string> {
    if (!this.token) {
      throw new Error('No token to refresh');
    }

    const response = await fetch(`${this.baseUrl}/api/auth/refresh`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to refresh token');
    }

    const { token }: { token: string } = await response.json();
    this.token = token;
    localStorage.setItem('auth_token', token);
    
    return token;
  }

  getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  hasPermission(permission: Permission): boolean {
    const userData = localStorage.getItem('user_data');
    if (!userData) return false;
    
    const user: User = JSON.parse(userData);
    return user.permissions.includes(permission);
  }

  isRole(role: UserRole): boolean {
    const userData = localStorage.getItem('user_data');
    if (!userData) return false;
    
    const user: User = JSON.parse(userData);
    return user.role === role;
  }

  canAccessClient(clientId: string): boolean {
    const userData = localStorage.getItem('user_data');
    if (!userData) return false;
    
    const user: User = JSON.parse(userData);
    return user.role === UserRole.SUPER_ADMIN || user.clientId === clientId;
  }

  getStoredUser(): User | null {
    const userData = localStorage.getItem('user_data');
    return userData ? JSON.parse(userData) : null;
  }
}
