const jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs');
const { v4: uuidv4 } = require('uuid');
const logger = require('../utils/logger');

class AuthService {
  constructor(cosmosDBService) {
    this.cosmosDBService = cosmosDBService;
    this.jwtSecret = process.env.JWT_SECRET || 'your-secret-key';
    this.jwtRefreshSecret = process.env.JWT_REFRESH_SECRET || 'your-refresh-secret';
    this.accessTokenExpiresIn = process.env.JWT_ACCESS_TOKEN_EXPIRES_IN || '15m';
    this.refreshTokenExpiresIn = process.env.JWT_REFRESH_TOKEN_EXPIRES_IN || '7d';
  }
  
  async login(username, password, deviceInfo) {
    try {
      logger.info('Login attempt', { username });
      
      // Find user
      const user = await this.cosmosDBService.findUserByUsername(username);
      if (!user) {
        logger.warn('Login failed - user not found', { username });
        throw new Error('Invalid credentials');
      }
      
      // Check if account is locked
      if (user.security.lockedUntil && new Date(user.security.lockedUntil) > new Date()) {
        logger.warn('Login failed - account locked', { username, lockedUntil: user.security.lockedUntil });
        throw new Error('Account locked. Try again later.');
      }
      
      // Check password
      const isValidPassword = await bcrypt.compare(password, user.password);
      if (!isValidPassword) {
        logger.warn('Login failed - invalid password', { username });
        await this.cosmosDBService.handleFailedLogin(username);
        throw new Error('Invalid credentials');
      }
      
      // Generate tokens
      const tokens = this.generateTokens(user);
      
      // Create session
      const sessionData = {
        sessionId: uuidv4(),
        userId: user.id,
        refreshToken: tokens.refreshToken,
        deviceInfo: deviceInfo || {
          userAgent: '',
          ip: '',
          platform: '',
          browser: '',
          version: ''
        },
        ipAddress: deviceInfo?.ip || ''
      };
      
      await this.cosmosDBService.createSession(sessionData);
      
      // Update last login
      await this.cosmosDBService.updateUserLastLogin(user.id);
      
      // Log audit event
      await this.cosmosDBService.logAuditEvent({
        userId: user.id,
        action: 'login',
        resource: 'auth',
        details: { 
          success: true, 
          deviceInfo: deviceInfo,
          loginTime: new Date().toISOString()
        },
        severity: 'info',
        category: 'authentication'
      });
      
      logger.info('Login successful', { 
        userId: user.id,
        username: user.username,
        role: user.role 
      });
      
      return {
        user: {
          id: user.id,
          username: user.username,
          email: user.email,
          role: user.role,
          profile: user.profile,
          permissions: user.permissions
        },
        tokens
      };
      
    } catch (error) {
      logger.error('Login failed', { error: error.message, username });
      
      // Log failed login attempt
      await this.cosmosDBService.logAuditEvent({
        userId: username, // Use username as userId for failed attempts
        action: 'login_failed',
        resource: 'auth',
        details: { 
          success: false, 
          error: error.message,
          deviceInfo: deviceInfo
        },
        severity: 'warning',
        category: 'authentication'
      });
      
      throw error;
    }
  }
  
  generateTokens(user) {
    const accessToken = jwt.sign(
      { 
        userId: user.id, 
        username: user.username, 
        role: user.role,
        permissions: user.permissions 
      },
      this.jwtSecret,
      { expiresIn: this.accessTokenExpiresIn }
    );
    
    const refreshToken = jwt.sign(
      { 
        userId: user.id, 
        sessionId: uuidv4(),
        tokenType: 'refresh'
      },
      this.jwtRefreshSecret,
      { expiresIn: this.refreshTokenExpiresIn }
    );
    
    return { accessToken, refreshToken };
  }
  
  async refreshToken(refreshToken) {
    try {
      logger.info('Token refresh attempt');
      
      // Verify refresh token
      const decoded = jwt.verify(refreshToken, this.jwtRefreshSecret);
      
      // Find session
      const session = await this.cosmosDBService.findSession(refreshToken);
      if (!session || !session.sessionData.isActive) {
        logger.warn('Token refresh failed - invalid session');
        throw new Error('Invalid refresh token');
      }
      
      // Find user
      const user = await this.cosmosDBService.findUserById(decoded.userId);
      if (!user || !user.security.isActive) {
        logger.warn('Token refresh failed - user not found or inactive');
        throw new Error('User not found or inactive');
      }
      
      // Generate new tokens
      const tokens = this.generateTokens(user);
      
      // Update session with new refresh token
      await this.cosmosDBService.updateSession(session.id, {
        refreshToken: tokens.refreshToken,
        'sessionData.lastActivity': new Date().toISOString()
      });
      
      // Log audit event
      await this.cosmosDBService.logAuditEvent({
        userId: user.id,
        action: 'token_refresh',
        resource: 'auth',
        details: { 
          sessionId: session.id,
          refreshTime: new Date().toISOString()
        },
        severity: 'info',
        category: 'authentication'
      });
      
      logger.info('Token refresh successful', { userId: user.id });
      
      return tokens;
      
    } catch (error) {
      logger.error('Token refresh failed', { error: error.message });
      
      if (error.name === 'JsonWebTokenError' || error.name === 'TokenExpiredError') {
        throw new Error('Invalid refresh token');
      }
      
      throw error;
    }
  }
  
  async logout(refreshToken, userId) {
    try {
      logger.info('Logout attempt', { userId });
      
      const session = await this.cosmosDBService.findSession(refreshToken);
      if (session) {
        // Deactivate session
        await this.cosmosDBService.updateSession(session.id, {
          'sessionData.isActive': false,
          'sessionData.loggedOutAt': new Date().toISOString()
        });
        
        // Log audit event
        await this.cosmosDBService.logAuditEvent({
          userId: userId,
          action: 'logout',
          resource: 'auth',
          details: { 
            sessionId: session.id,
            logoutTime: new Date().toISOString()
          },
          severity: 'info',
          category: 'authentication'
        });
        
        logger.info('Logout successful', { userId, sessionId: session.id });
      }
      
      return true;
    } catch (error) {
      logger.error('Logout failed', { error: error.message, userId });
      return false;
    }
  }
  
  async validateToken(token) {
    try {
      const decoded = jwt.verify(token, this.jwtSecret);
      
      // Check if user still exists and is active
      const user = await this.cosmosDBService.findUserById(decoded.userId);
      if (!user || !user.security.isActive) {
        throw new Error('User not found or inactive');
      }
      
      return {
        userId: decoded.userId,
        username: decoded.username,
        role: decoded.role,
        permissions: decoded.permissions
      };
    } catch (error) {
      logger.error('Token validation failed', { error: error.message });
      throw new Error('Invalid token');
    }
  }
  
  async revokeAllSessions(userId) {
    try {
      logger.info('Revoking all sessions', { userId });
      
      // This would typically involve updating all active sessions for the user
      // For now, we'll just log the action
      await this.cosmosDBService.logAuditEvent({
        userId: userId,
        action: 'revoke_all_sessions',
        resource: 'auth',
        details: { 
          revokeTime: new Date().toISOString()
        },
        severity: 'warning',
        category: 'authentication'
      });
      
      logger.info('All sessions revoked', { userId });
      return true;
    } catch (error) {
      logger.error('Failed to revoke all sessions', { error: error.message, userId });
      return false;
    }
  }
  
  hasPermission(userPermissions, requiredPermission) {
    return userPermissions.includes(requiredPermission);
  }
  
  hasRole(userRole, requiredRole) {
    return userRole === requiredRole;
  }
  
  canAccessResource(user, resource, action) {
    // Simple role-based access control
    const permissions = {
      fleet_manager: {
        robots: ['read', 'write', 'command'],
        alerts: ['read', 'write', 'acknowledge', 'resolve'],
        system: ['read', 'health'],
        reports: ['read', 'export']
      },
      technical_engineer: {
        robots: ['read', 'write'],
        alerts: ['read', 'write'],
        system: ['read', 'health'],
        reports: ['read']
      },
      warehouse_manager: {
        robots: ['read', 'command'],
        alerts: ['read', 'acknowledge'],
        reports: ['read']
      }
    };
    
    const userPermissions = permissions[user.role] || {};
    const resourcePermissions = userPermissions[resource] || [];
    
    return resourcePermissions.includes(action);
  }
}

module.exports = AuthService;
