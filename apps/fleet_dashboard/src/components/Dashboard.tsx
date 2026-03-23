import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { Robot, Alert, RobotCommand } from '../types/robot';
import { robotService, alertService } from '../services/robotApi';

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

export const Dashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const [robots, setRobots] = useState<Robot[]>([]);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchRobotData();
    const interval = setInterval(fetchRobotData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchRobotData = async () => {
    try {
      const [robotsData, alertsData] = await Promise.all([
        robotService.getAllRobots(),
        alertService.getAlerts()
      ]);

      setRobots(Object.values(robotsData));
      setAlerts(alertsData);
      setLoading(false);
      setError(null);
    } catch (error: any) {
      console.error('Failed to fetch robot data:', error);
      setError('Failed to fetch robot data');
      setLoading(false);
    }
  };

  const handleCommand = async (robotId: string, command: RobotCommand) => {
    try {
      await robotService.sendCommand(robotId, command);
      fetchRobotData();
    } catch (error: any) {
      console.error('Failed to send command:', error);
    }
  };

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await alertService.acknowledgeAlert(alertId);
      fetchRobotData();
    } catch (error: any) {
      console.error('Failed to acknowledge alert:', error);
    }
  };

  const handleResolveAlert = async (alertId: string) => {
    try {
      await alertService.resolveAlert(alertId);
      fetchRobotData();
    } catch (error: any) {
      console.error('Failed to resolve alert:', error);
    }
  };

  if (loading) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(255, 255, 255, 0.95)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000
      }}>
        <div style={{ textAlign: 'center' }}>
          <div style={{
            width: '60px',
            height: '60px',
            border: '4px solid #e2e8f0',
            borderTop: '4px solid #0ea5e9',
            borderRadius: '50%',
            animation: 'spin 1s linear infinite',
            margin: '0 auto 1rem'
          }} />
          <div style={{
            fontSize: designSystem.typography.lg,
            color: designSystem.colors.primary[600],
            fontWeight: 500
          }}>
            Initializing Fleet Dashboard...
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{
      background: designSystem.colors.gray[50],
      minHeight: '100vh',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      color: designSystem.colors.gray[900]
    }}>
      {/* Modern Header */}
      <header style={{
        background: '#ffffff',
        borderBottom: `1px solid ${designSystem.colors.gray[200]}`,
        padding: '1.5rem 2rem',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        backdropFilter: 'blur(8px)',
        backgroundColor: 'rgba(255, 255, 255, 0.95)'
      }}>
        <div style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          maxWidth: '1400px',
          margin: '0 auto'
        }}>
          <div>
            <h1 style={{
              fontSize: designSystem.typography['2xl'],
              fontWeight: 700,
              color: designSystem.colors.gray[900],
              margin: 0,
              letterSpacing: '-0.025em'
            }}>
              Fleet Control
            </h1>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: designSystem.spacing.md,
              marginTop: designSystem.spacing.xs
            }}>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: designSystem.spacing.sm,
                padding: `${designSystem.spacing.xs} ${designSystem.spacing.md}`,
                background: designSystem.colors.success,
                color: 'white',
                borderRadius: '9999px',
                fontSize: designSystem.typography.xs,
                fontWeight: 500
              }}>
                <svg width="8" height="8" viewBox="0 0 8 8" fill="none">
                  <circle cx="4" cy="4" r="3" fill="white" />
                </svg>
                System Online
              </span>
              <span style={{
                fontSize: designSystem.typography.sm,
                color: designSystem.colors.gray[500]
              }}>
                Last sync: {new Date().toLocaleTimeString()}
              </span>
            </div>
          </div>
          
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: designSystem.spacing.lg
          }}>
            <span style={{
              fontSize: designSystem.typography.sm,
              color: designSystem.colors.gray[600]
            }}>
              {user?.profile?.firstName} {user?.profile?.lastName}
            </span>
            <button
              onClick={logout}
              style={{
                padding: `${designSystem.spacing.sm} ${designSystem.spacing.lg}`,
                background: designSystem.colors.gray[100],
                color: designSystem.colors.gray[700],
                border: `1px solid ${designSystem.colors.gray[200]}`,
                borderRadius: designSystem.spacing.sm,
                fontSize: designSystem.typography.sm,
                fontWeight: 500,
                cursor: 'pointer',
                transition: 'all 0.2s ease'
              }}
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      {/* Error Notification */}
      {error && (
        <div style={{
          position: 'fixed',
          top: '20px',
          right: '20px',
          background: designSystem.colors.error,
          color: 'white',
          padding: '12px 20px',
          borderRadius: '8px',
          boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
          zIndex: 1000,
          maxWidth: '300px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span>⚠️</span>
            <span>Connection Error</span>
          </div>
          <div style={{ fontSize: '12px', marginTop: '8px' }}>
            {error}
          </div>
          <button
            onClick={fetchRobotData}
            style={{
              background: 'white',
              color: designSystem.colors.error,
              border: '1px solid white',
              padding: '6px 12px',
              borderRadius: '4px',
              cursor: 'pointer',
              marginTop: '10px'
            }}
          >
            Retry
          </button>
        </div>
      )}

      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '0 2rem' }}>

        {/* Modern Metrics Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
          gap: designSystem.spacing.xl,
          marginBottom: designSystem.spacing['2xl']
        }}>
          {[
            { label: 'Total Robots', value: robots.length, icon: 'M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z', color: designSystem.colors.primary[500] },
            { label: 'Online', value: robots.filter(r => r.status === 'active').length, icon: 'M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z', color: designSystem.colors.success },
            { label: 'Critical Alerts', value: alerts.filter(a => !a.resolved && a.severity === 'critical').length, icon: 'M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 15.5c-.77.833.192 2.5 1.732 2.5z', color: designSystem.colors.error },
            { label: 'Avg Battery', value: robots.length > 0 ? `${Math.round(robots.reduce((sum, r) => sum + r.battery_level, 0) / robots.length)}%` : '0%', icon: 'M13 2H3a2 2 0 00-2 2v16a2 2 0 002 2h10a2 2 0 002-2V4a2 2 0 00-2-2zM7 20a1 1 0 110-2 1 1 0 010 2zm5-3H5V5h7v12z', color: designSystem.colors.warning }
          ].map((metric, index) => (
            <div key={index} style={{
              background: designSystem.colors.gray[100],
              border: `1px solid ${designSystem.colors.gray[200]}`,
              borderRadius: '12px',
              padding: designSystem.spacing.xl,
              transition: 'all 0.2s ease',
              boxShadow: designSystem.shadows.sm,
              position: 'relative',
              overflow: 'hidden'
            }}>
              <div style={{
                position: 'absolute',
                top: '0',
                left: '0',
                right: '0',
                height: '3px',
                background: `linear-gradient(90deg, ${metric.color} 0%, ${metric.color}dd 100%)`
              }} />
              <div style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'flex-start',
                marginBottom: designSystem.spacing.lg
              }}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" style={{ color: metric.color }}>
                  <path d={metric.icon} fill="currentColor" />
                </svg>
                <div style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  background: metric.color
                }} />
              </div>
              <div style={{
                fontSize: designSystem.typography['2xl'],
                fontWeight: 700,
                color: designSystem.colors.gray[900],
                marginBottom: designSystem.spacing.xs
              }}>
                {metric.value}
              </div>
              <div style={{
                fontSize: designSystem.typography.sm,
                color: designSystem.colors.gray[600],
                fontWeight: 500
              }}>
                {metric.label}
              </div>
            </div>
          ))}
        </div>

        {/* Modern Alert Section */}
        <div style={{
          background: '#ffffff',
          border: `1px solid ${designSystem.colors.gray[200]}`,
          borderRadius: '0.75rem',
          padding: designSystem.spacing.xl,
          marginBottom: designSystem.spacing['2xl']
        }}>
          <div style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            marginBottom: designSystem.spacing.lg
          }}>
            <h2 style={{
              fontSize: designSystem.typography.xl,
              fontWeight: 600,
              color: designSystem.colors.gray[900],
              margin: 0
            }}>
              Active Alerts
            </h2>
            <span style={{
              padding: `${designSystem.spacing.xs} ${designSystem.spacing.md}`,
              background: designSystem.colors.error,
              color: 'white',
              borderRadius: '9999px',
              fontSize: designSystem.typography.xs,
              fontWeight: 500
            }}>
              {alerts.filter(a => !a.resolved).length}
            </span>
          </div>

          {alerts.filter(a => !a.resolved).length === 0 ? (
            <div style={{
              textAlign: 'center',
              padding: designSystem.spacing['2xl'],
              color: designSystem.colors.gray[500]
            }}>
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" style={{ margin: '0 auto', marginBottom: designSystem.spacing.lg }}>
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" stroke={designSystem.colors.success} strokeWidth="2" fill="none" />
              </svg>
              <p style={{ margin: 0, fontSize: designSystem.typography.sm }}>
                No active alerts
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: designSystem.spacing.md }}>
              {alerts.filter(a => !a.resolved).map(alert => (
                <div key={alert.id} style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: designSystem.spacing.lg,
                  background: alert.severity === 'critical' ? 'rgba(239, 68, 68, 0.05)' : 'rgba(245, 158, 11, 0.05)',
                  border: `1px solid ${alert.severity === 'critical' ? designSystem.colors.error : designSystem.colors.warning}`,
                  borderRadius: designSystem.spacing.sm
                }}>
                  <div>
                    <div style={{
                      fontWeight: 500,
                      color: designSystem.colors.gray[900],
                      marginBottom: designSystem.spacing.xs
                    }}>
                      {alert.robotId}
                    </div>
                    <div style={{
                      fontSize: designSystem.typography.sm,
                      color: designSystem.colors.gray[600]
                    }}>
                      {alert.message}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: designSystem.spacing.sm }}>
                    {!alert.acknowledged && (
                      <button
                        onClick={() => handleAcknowledgeAlert(alert.id)}
                        style={{
                          padding: `${designSystem.spacing.sm} ${designSystem.spacing.lg}`,
                          background: designSystem.colors.warning,
                          color: 'white',
                          border: 'none',
                          borderRadius: designSystem.spacing.xs,
                          fontSize: designSystem.typography.xs,
                          fontWeight: 500,
                          cursor: 'pointer'
                        }}
                      >
                        Acknowledge
                      </button>
                    )}
                    <button
                      onClick={() => handleResolveAlert(alert.id)}
                      style={{
                        padding: `${designSystem.spacing.sm} ${designSystem.spacing.lg}`,
                        background: designSystem.colors.success,
                        color: 'white',
                        border: 'none',
                        borderRadius: designSystem.spacing.xs,
                        fontSize: designSystem.typography.xs,
                        fontWeight: 500,
                        cursor: 'pointer'
                      }}
                    >
                      Resolve
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
        {/* Modern Robot Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: designSystem.spacing.xl
        }}>
          {robots.map(robot => (
            <div key={robot.robotId} style={{
              background: designSystem.colors.gray[100],
              border: `1px solid ${designSystem.colors.gray[200]}`,
              borderRadius: '12px',
              padding: designSystem.spacing.xl,
              transition: 'all 0.2s ease',
              boxShadow: designSystem.shadows.sm,
              position: 'relative',
              overflow: 'hidden'
            }}>
              {/* Status Indicator */}
              <div style={{
                position: 'absolute',
                top: designSystem.spacing.lg,
                right: designSystem.spacing.lg,
                display: 'flex',
                alignItems: 'center',
                gap: designSystem.spacing.sm
              }}>
                <div style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  background: robot.status === 'active' ? designSystem.colors.success : designSystem.colors.warning,
                  animation: robot.status === 'active' ? 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' : 'none'
                }} />
                <span style={{
                  fontSize: designSystem.typography.xs,
                  fontWeight: 500,
                  color: robot.status === 'active' ? designSystem.colors.success : designSystem.colors.warning,
                  textTransform: 'uppercase',
                  letterSpacing: '0.05em'
                }}>
                  {robot.status}
                </span>
              </div>

              {/* Robot Info */}
              <div style={{ marginBottom: designSystem.spacing.lg }}>
                <h3 style={{
                  fontSize: designSystem.typography.lg,
                  fontWeight: 600,
                  color: designSystem.colors.gray[900],
                  margin: `0 0 ${designSystem.spacing.sm} 0`
                }}>
                  {robot.robotId}
                </h3>
                <p style={{
                  fontSize: designSystem.typography.sm,
                  color: designSystem.colors.gray[600],
                  margin: 0
                }}>
                  Unit ID: {robot.robotId}
                </p>
              </div>

              {/* Metrics Grid */}
              <div style={{
                display: 'grid',
                gridTemplateColumns: '1fr 1fr',
                gap: designSystem.spacing.lg,
                marginBottom: designSystem.spacing.lg
              }}>
                <div>
                  <div style={{
                    fontSize: designSystem.typography.xs,
                    color: designSystem.colors.gray[500],
                    marginBottom: designSystem.spacing.xs,
                    fontWeight: 500
                  }}>
                    Battery Level
                  </div>
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: designSystem.spacing.sm
                  }}>
                    <div style={{
                      width: '100%',
                      height: '6px',
                      backgroundColor: designSystem.colors.gray[200],
                      borderRadius: '3px',
                      overflow: 'hidden'
                    }}>
                      <div style={{
                        width: `${robot.battery_level}%`,
                        height: '100%',
                        background: robot.battery_level > 50 ? designSystem.colors.success : 
                                   robot.battery_level > 20 ? designSystem.colors.warning : designSystem.colors.error,
                        borderRadius: '3px',
                        transition: 'width 0.3s ease'
                      }} />
                    </div>
                    <span style={{
                      fontSize: designSystem.typography.sm,
                      fontWeight: 500,
                      color: designSystem.colors.gray[700]
                    }}>
                      {robot.battery_level}%
                    </span>
                  </div>
                </div>

                <div>
                  <div style={{
                    fontSize: designSystem.typography.xs,
                    color: designSystem.colors.gray[500],
                    marginBottom: designSystem.spacing.xs,
                    fontWeight: 500
                  }}>
                    Temperature
                  </div>
                  <div style={{
                    fontSize: designSystem.typography.sm,
                    fontWeight: 500,
                    color: designSystem.colors.gray[700]
                  }}>
                    {robot.temperature}°C
                  </div>
                </div>
              </div>

              {/* Position */}
              <div style={{ marginBottom: designSystem.spacing.lg }}>
                <div style={{
                  fontSize: designSystem.typography.xs,
                  color: designSystem.colors.gray[500],
                  marginBottom: designSystem.spacing.xs,
                  fontWeight: 500
                }}>
                  Current Position
                </div>
                <div style={{
                  fontSize: designSystem.typography.sm,
                  fontFamily: 'SF Mono, Monaco, "Cascadia Code", "Roboto Mono", Consolas, "Courier New", monospace',
                  color: designSystem.colors.gray[700],
                  background: designSystem.colors.gray[200],
                  padding: designSystem.spacing.sm,
                  borderRadius: designSystem.spacing.xs
                }}>
                  ({robot.position.x}, {robot.position.y}, {robot.position.z})
                </div>
              </div>

              {/* Action Button */}
              <button
                onClick={() => handleCommand(robot.robotId, { command: 'move_to', parameters: { x: 0, y: 0, z: 0 } })}
                style={{
                  width: '100%',
                  padding: `${designSystem.spacing.sm} ${designSystem.spacing.lg}`,
                  background: designSystem.colors.primary[500],
                  color: 'white',
                  border: 'none',
                  borderRadius: designSystem.spacing.sm,
                  fontSize: designSystem.typography.sm,
                  fontWeight: 500,
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  boxShadow: designSystem.shadows.sm
                }}
              >
                Send Command
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
