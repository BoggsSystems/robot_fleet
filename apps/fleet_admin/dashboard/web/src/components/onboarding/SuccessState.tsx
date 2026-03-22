import { CheckCircle, Rocket, LayoutDashboard, Plus, Settings } from 'lucide-react';
import type { RobotConfig } from './OnboardingWizard';

interface SuccessStateProps {
  config: RobotConfig;
  onFinish: (config: RobotConfig) => void;
}

export function SuccessState({ config, onFinish }: SuccessStateProps) {
  const handleAction = (action: string) => {
    // Store action preference before finishing
    localStorage.setItem('onboarding_action', action);
    onFinish(config);
  };

  return (
    <div className="success-container">
      <div className="success-icon-large">
        <CheckCircle size={64} />
      </div>

      <h1>Onboarding Complete!</h1>
      <p className="success-message">
        🎉 <strong>{config.name}</strong> is now ready for duty!
      </p>

      <div className="summary-card">
        <h3>Robot Summary</h3>
        <div className="summary-grid">
          <div className="summary-item">
            <span className="label">Name:</span>
            <span className="value">{config.name}</span>
          </div>
          <div className="summary-item">
            <span className="label">ID:</span>
            <span className="value">{config.robotId}</span>
          </div>
          <div className="summary-item">
            <span className="label">Zone:</span>
            <span className="value">{config.zone} / {config.subZone}</span>
          </div>
          <div className="summary-item">
            <span className="label">IP:</span>
            <span className="value">{config.ipAddress}</span>
          </div>
          <div className="summary-item">
            <span className="label">Status:</span>
            <span className="value status-online">ONLINE</span>
          </div>
          <div className="summary-item">
            <span className="label">Capabilities:</span>
            <span className="value">{config.capabilities?.length || 0} assigned</span>
          </div>
        </div>
      </div>

      <div className="next-actions">
        <h3>What's next?</h3>
        <div className="action-buttons">
          <button 
            className="action-card primary"
            onClick={() => handleAction('assign')}
          >
            <Rocket size={24} />
            <span>Assign First Task</span>
          </button>

          <button 
            className="action-card"
            onClick={() => handleAction('dashboard')}
          >
            <LayoutDashboard size={24} />
            <span>View Fleet Dashboard</span>
          </button>

          <button 
            className="action-card"
            onClick={() => handleAction('schedule')}
          >
            <Settings size={24} />
            <span>Configure Auto-Schedule</span>
          </button>

          <button 
            className="action-card"
            onClick={() => handleAction('add')}
          >
            <Plus size={24} />
            <span>Add Another Robot</span>
          </button>
        </div>
      </div>
    </div>
  );
}
