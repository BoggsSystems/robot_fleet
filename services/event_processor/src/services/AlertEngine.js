const logger = require('../utils/logger');
const TelemetryValidator = require('../utils/TelemetryValidator');

class AlertEngine {
  constructor() {
    this.alerts = new Map();
    this.alertThresholds = {
      batteryLow: parseFloat(process.env.BATTERY_LOW_THRESHOLD) || 20,
      temperatureHigh: parseFloat(process.env.TEMPERATURE_HIGH_THRESHOLD) || 80,
      connectionTimeout: parseInt(process.env.CONNECTION_TIMEOUT_SECONDS) || 30,
      errorRateThreshold: parseFloat(process.env.ERROR_RATE_THRESHOLD) || 0.1
    };
    this.robotLastSeen = new Map();
    this.robotErrorCounts = new Map();
  }
  
  processTelemetry(telemetry) {
    const alerts = [];
    const robotId = telemetry.robotId;
    const timestamp = new Date(telemetry.timestamp);
    
    // Update last seen time
    this.robotLastSeen.set(robotId, timestamp);
    
    // Check battery level
    if (telemetry.battery_level < this.alertThresholds.batteryLow) {
      const alert = this.createAlert(robotId, 'battery_low', {
        batteryLevel: telemetry.battery_level,
        threshold: this.alertThresholds.batteryLow
      });
      alerts.push(alert);
    }
    
    // Check temperature
    if (telemetry.temperature > this.alertThresholds.temperatureHigh) {
      const alert = this.createAlert(robotId, 'temperature_high', {
        temperature: telemetry.temperature,
        threshold: this.alertThresholds.temperatureHigh
      });
      alerts.push(alert);
    }
    
    // Check robot status
    if (telemetry.status === 'error') {
      const alert = this.createAlert(robotId, 'robot_error', {
        status: telemetry.status,
        errors: telemetry.errors
      });
      alerts.push(alert);
    }
    
    // Check for connection timeout
    const lastSeen = this.robotLastSeen.get(robotId);
    if (lastSeen) {
      const timeSinceLastSeen = (Date.now() - lastSeen.getTime()) / 1000;
      if (timeSinceLastSeen > this.alertThresholds.connectionTimeout) {
        const alert = this.createAlert(robotId, 'connection_timeout', {
          lastSeen: lastSeen.toISOString(),
          timeSinceLastSeen: timeSinceLastSeen
        });
        alerts.push(alert);
      }
    }
    
    // Check error rate
    if (telemetry.errors && telemetry.errors.length > 0) {
      const errorCount = this.robotErrorCounts.get(robotId) || 0;
      this.robotErrorCounts.set(robotId, errorCount + telemetry.errors.length);
      
      // Simple error rate calculation (could be more sophisticated)
      const totalTelemetryCount = 100; // This should be tracked properly
      const errorRate = this.robotErrorCounts.get(robotId) / totalTelemetryCount;
      
      if (errorRate > this.alertThresholds.errorRateThreshold) {
        const alert = this.createAlert(robotId, 'high_error_rate', {
          errorRate: errorRate,
          threshold: this.alertThresholds.errorRateThreshold,
          errorCount: this.robotErrorCounts.get(robotId)
        });
        alerts.push(alert);
      }
    }
    
    // Log alerts
    if (alerts.length > 0) {
      logger.warn('Alerts generated', { 
        robotId, 
        alertCount: alerts.length,
        alerts: alerts.map(a => ({ type: a.type, severity: a.severity }))
      });
    }
    
    return alerts;
  }
  
  createAlert(robotId, alertType, details) {
    const alertId = `${robotId}-${alertType}-${Date.now()}`;
    const alert = {
      id: alertId,
      robotId: robotId,
      type: alertType,
      severity: this.getSeverity(alertType, details),
      timestamp: new Date().toISOString(),
      details: details,
      acknowledged: false,
      resolved: false
    };
    
    // Store alert
    this.alerts.set(alertId, alert);
    
    logger.warn('Alert created', { 
      alertId, 
      robotId, 
      alertType, 
      severity: alert.severity 
    });
    
    return alert;
  }
  
  getSeverity(alertType, details) {
    switch (alertType) {
      case 'battery_low':
        return details.batteryLevel < 10 ? 'critical' : 'warning';
      case 'temperature_high':
        return details.temperature > 90 ? 'critical' : 'warning';
      case 'robot_error':
        return 'error';
      case 'connection_timeout':
        return 'critical';
      case 'high_error_rate':
        return details.errorRate > 0.5 ? 'critical' : 'warning';
      default:
        return 'info';
    }
  }
  
  getActiveAlerts(robotId = null) {
    const activeAlerts = Array.from(this.alerts.values()).filter(alert => !alert.resolved);
    
    if (robotId) {
      return activeAlerts.filter(alert => alert.robotId === robotId);
    }
    
    return activeAlerts;
  }
  
  acknowledgeAlert(alertId) {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.acknowledged = true;
      alert.acknowledgedAt = new Date().toISOString();
      
      logger.info('Alert acknowledged', { alertId });
      return true;
    }
    
    return false;
  }
  
  resolveAlert(alertId) {
    const alert = this.alerts.get(alertId);
    if (alert) {
      alert.resolved = true;
      alert.resolvedAt = new Date().toISOString();
      
      logger.info('Alert resolved', { alertId });
      return true;
    }
    
    return false;
  }
  
  getAlertStatistics() {
    const alerts = Array.from(this.alerts.values());
    const activeAlerts = alerts.filter(alert => !alert.resolved);
    const criticalAlerts = activeAlerts.filter(alert => alert.severity === 'critical');
    const warningAlerts = activeAlerts.filter(alert => alert.severity === 'warning');
    const errorAlerts = activeAlerts.filter(alert => alert.severity === 'error');
    
    // Group by robot
    const alertsByRobot = {};
    for (const alert of activeAlerts) {
      if (!alertsByRobot[alert.robotId]) {
        alertsByRobot[alert.robotId] = [];
      }
      alertsByRobot[alert.robotId].push(alert);
    }
    
    // Group by type
    const alertsByType = {};
    for (const alert of activeAlerts) {
      if (!alertsByType[alert.type]) {
        alertsByType[alert.type] = 0;
      }
      alertsByType[alert.type]++;
    }
    
    return {
      total: alerts.length,
      active: activeAlerts.length,
      critical: criticalAlerts.length,
      warning: warningAlerts.length,
      error: errorAlerts.length,
      byRobot: alertsByRobot,
      byType: alertsByType,
      thresholds: this.alertThresholds
    };
  }
  
  checkConnectionTimeouts() {
    const alerts = [];
    const now = Date.now();
    
    for (const [robotId, lastSeen] of this.robotLastSeen.entries()) {
      const timeSinceLastSeen = (now - lastSeen.getTime()) / 1000;
      
      if (timeSinceLastSeen > this.alertThresholds.connectionTimeout) {
        const alert = this.createAlert(robotId, 'connection_timeout', {
          lastSeen: lastSeen.toISOString(),
          timeSinceLastSeen: timeSinceLastSeen
        });
        alerts.push(alert);
      }
    }
    
    return alerts;
  }
  
  resetRobotMetrics(robotId) {
    this.robotLastSeen.delete(robotId);
    this.robotErrorCounts.delete(robotId);
    
    // Resolve any active alerts for this robot
    const robotAlerts = this.getActiveAlerts(robotId);
    for (const alert of robotAlerts) {
      this.resolveAlert(alert.id);
    }
    
    logger.info('Reset robot metrics', { robotId });
  }
  
  updateThresholds(newThresholds) {
    this.alertThresholds = { ...this.alertThresholds, ...newThresholds };
    
    logger.info('Updated alert thresholds', { thresholds: this.alertThresholds });
  }
  
  getRobotHealthScore(robotId) {
    const robotAlerts = this.getActiveAlerts(robotId);
    
    if (robotAlerts.length === 0) {
      return 100; // Perfect health
    }
    
    let score = 100;
    
    for (const alert of robotAlerts) {
      switch (alert.severity) {
        case 'critical':
          score -= 30;
          break;
        case 'error':
          score -= 20;
          break;
        case 'warning':
          score -= 10;
          break;
        case 'info':
          score -= 5;
          break;
      }
    }
    
    return Math.max(0, score);
  }
}

module.exports = AlertEngine;
