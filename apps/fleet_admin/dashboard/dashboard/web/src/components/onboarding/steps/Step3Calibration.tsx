import { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Activity, CheckCircle, AlertCircle, Loader2, Camera } from 'lucide-react';
import type { RobotConfig } from '../OnboardingWizard';

interface Step3CalibrationProps {
  config: Partial<RobotConfig>;
  calibrationComplete: boolean;
  setCalibrationComplete: (complete: boolean) => void;
  onNext: () => void;
  onBack: () => void;
}

type CalStep = 'diagnostics' | 'stand' | 'movement';

interface CalStatus {
  step: CalStep;
  status: 'pending' | 'running' | 'success' | 'error';
  message: string;
}

export function Step3Calibration({
  config,
  calibrationComplete,
  setCalibrationComplete,
  onNext,
  onBack,
}: Step3CalibrationProps) {
  const [calStatuses, setCalStatuses] = useState<Record<CalStep, CalStatus>>({
    diagnostics: { step: 'diagnostics', status: 'pending', message: 'Ready to start' },
    stand: { step: 'stand', status: 'pending', message: 'Waiting...' },
    movement: { step: 'movement', status: 'pending', message: 'Waiting...' },
  });
  const [cameraExpanded, setCameraExpanded] = useState(false);

  const runStep = async (step: CalStep) => {
    setCalStatuses((prev) => ({
      ...prev,
      [step]: { ...prev[step], status: 'running', message: 'In progress...' },
    }));

    try {
      const response = await fetch('/api/robots/calibrate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          robotId: config.robotId,
          step,
          ip: config.ipAddress,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setCalStatuses((prev) => ({
          ...prev,
          [step]: { ...prev[step], status: 'success', message: data.message },
        }));
      } else {
        setCalStatuses((prev) => ({
          ...prev,
          [step]: { ...prev[step], status: 'error', message: data.error },
        }));
      }
    } catch (err) {
      setCalStatuses((prev) => ({
        ...prev,
        [step]: { ...prev[step], status: 'error', message: 'Connection failed' },
      }));
    }
  };

  useEffect(() => {
    const allSuccess = Object.values(calStatuses).every((s) => s.status === 'success');
    setCalibrationComplete(allSuccess);
  }, [calStatuses, setCalibrationComplete]);

  return (
    <div className="step-container">
      <h2>Step 3: Safety Calibration</h2>
      <p className="step-description">
        ⚠️ Ensure the area around the robot is clear before proceeding. The robot will perform
        self-diagnostics and test movements.
      </p>

      <div className="calibration-steps">
        <div className={`cal-step ${calStatuses.diagnostics.status}`}>
          <div className="cal-header">
            <input
              type="checkbox"
              checked={calStatuses.diagnostics.status === 'success'}
              readOnly
            />
            <span className="cal-title">1. Perform Self-Diagnostics</span>
            {calStatuses.diagnostics.status === 'running' && (
              <Loader2 className="spin" size={16} />
            )}
            {calStatuses.diagnostics.status === 'success' && (
              <CheckCircle className="success-icon" size={16} />
            )}
            {calStatuses.diagnostics.status === 'error' && (
              <AlertCircle className="error-icon" size={16} />
            )}
          </div>
          <p className="cal-message">{calStatuses.diagnostics.message}</p>
          {calStatuses.diagnostics.status === 'pending' && (
            <button onClick={() => runStep('diagnostics')} className="cal-button">
              <Activity size={14} />
              Run Diagnostics
            </button>
          )}
          {calStatuses.diagnostics.status === 'error' && (
            <button onClick={() => runStep('diagnostics')} className="cal-button retry">
              Retry
            </button>
          )}
        </div>

        <div className={`cal-step ${calStatuses.stand.status}`}>
          <div className="cal-header">
            <input
              type="checkbox"
              checked={calStatuses.stand.status === 'success'}
              readOnly
            />
            <span className="cal-title">2. Calibrate Standing Position</span>
            {calStatuses.stand.status === 'running' && <Loader2 className="spin" size={16} />}
            {calStatuses.stand.status === 'success' && <CheckCircle className="success-icon" size={16} />}
            {calStatuses.stand.status === 'error' && <AlertCircle className="error-icon" size={16} />}
          </div>
          <p className="cal-message">{calStatuses.stand.message}</p>
          {calStatuses.diagnostics.status === 'success' && calStatuses.stand.status === 'pending' && (
            <button onClick={() => runStep('stand')} className="cal-button">
              Calibrate Stand
            </button>
          )}
        </div>

        <div className={`cal-step ${calStatuses.movement.status}`}>
          <div className="cal-header">
            <input
              type="checkbox"
              checked={calStatuses.movement.status === 'success'}
              readOnly
            />
            <span className="cal-title">3. Test Basic Movements</span>
            {calStatuses.movement.status === 'running' && <Loader2 className="spin" size={16} />}
            {calStatuses.movement.status === 'success' && <CheckCircle className="success-icon" size={16} />}
            {calStatuses.movement.status === 'error' && <AlertCircle className="error-icon" size={16} />}
          </div>
          <p className="cal-message">{calStatuses.movement.message}</p>
          {calStatuses.stand.status === 'success' && calStatuses.movement.status === 'pending' && (
            <button onClick={() => runStep('movement')} className="cal-button">
              Test Movement
            </button>
          )}
        </div>
      </div>

      <div className="camera-section">
        <div 
          className="camera-header"
          onClick={() => setCameraExpanded(!cameraExpanded)}
        >
          <Camera size={16} />
          <span>Live Camera Feed</span>
          <span className="camera-status">Standby</span>
        </div>
        {cameraExpanded && (
          <div className="camera-feed">
            <div className="camera-placeholder">
              <Camera size={48} />
              <p>Robot camera feed will appear here</p>
              <span>Click to expand</span>
            </div>
          </div>
        )}
      </div>

      <div className="step-actions">
        <button onClick={onBack} className="btn-secondary">
          <ChevronLeft size={16} />
          Back
        </button>
        <button 
          onClick={onNext} 
          className="btn-primary"
          disabled={!calibrationComplete}
        >
          Continue
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
