export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  profile: {
    firstName: string;
    lastName: string;
    department: string;
    phone: string;
    timezone: string;
    preferences: {
      theme: string;
      notifications: boolean;
      autoRefresh: number;
      language: string;
    };
  };
  permissions: string[];
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface AuthContextType extends AuthState {
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthResponse {
  success: boolean;
  user: User;
  tokens: {
    accessToken: string;
    refreshToken: string;
  };
}

export interface TokenResponse {
  success: boolean;
  tokens: {
    accessToken: string;
    refreshToken: string;
  };
}
