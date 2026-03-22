import { useState, useCallback } from 'react';
import { Step1Discovery } from './steps/Step1Discovery';
import { Step2Identity } from './steps/Step2Identity';
import { Step3Calibration } from './steps/Step3Calibration';
import { Step4Simulation } from './steps/Step4Simulation';
import { SuccessState } from './SuccessState';
import './OnboardingWizard.css';

export type Fleet = {
  id: string;
  name: string;
  description: string;
  location: string;
  robotCount: number;
  createdAt: string;
};

export type RobotConfig = {
  robotId: string;
  name: string;
  ipAddress: string;
  networkInterface: string;
  zone: string;
  subZone: string;
  capabilities: string[];
  model: string;
  serial: string;
  firmware: string;
  robotType: string;
  robotCategory: string;
  vendor: string;
  fleetId: string;
};

export type OnboardingState = {
  step: number;
  config: Partial<RobotConfig>;
  connectionTested: boolean;
  calibrationComplete: boolean;
  simulationRun: boolean;
};

interface OnboardingWizardProps {
  onComplete: (config: RobotConfig) => void;
  onCancel: () => void;
  existingRobots?: string[];
}

export function OnboardingWizard({ onComplete, onCancel, existingRobots = [] }: OnboardingWizardProps) {
  const [state, setState] = useState<OnboardingState>({
    step: 1,
    config: {},
    connectionTested: false,
    calibrationComplete: false,
    simulationRun: false,
  });

  const updateConfig = useCallback((updates: Partial<RobotConfig>) => {
    setState(prev => ({
      ...prev,
      config: { ...prev.config, ...updates },
    }));
  }, []);

  const nextStep = useCallback(() => {
    setState(prev => ({ ...prev, step: prev.step + 1 }));
  }, []);

  const prevStep = useCallback(() => {
    setState(prev => ({ ...prev, step: prev.step - 1 }));
  }, []);

  const handleComplete = useCallback(() => {
    if (state.config.robotId && state.config.name && state.config.ipAddress) {
      onComplete(state.config as RobotConfig);
    }
  }, [state.config, onComplete]);

  const progress = ((state.step - 1) / 4) * 100;

  return (
    <div className="onboarding-overlay">
      <div className="onboarding-container">
        <div className="onboarding-header">
          <h1>🤖 Onboard New Robot</h1>
          <span className="step-indicator">Step {state.step} of 4</span>
        </div>

        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress}%` }}
          />
        </div>

        <div className="onboarding-content">
          {state.step === 1 && (
            <Step1Discovery
              config={state.config}
              updateConfig={updateConfig}
              connectionTested={state.connectionTested}
              setConnectionTested={(tested) => setState(prev => ({ ...prev, connectionTested: tested }))}
              onNext={nextStep}
              onCancel={onCancel}
            />
          )}

          {state.step === 2 && (
            <Step2Identity
              config={state.config}
              updateConfig={updateConfig}
              existingRobots={existingRobots}
              onNext={nextStep}
              onBack={prevStep}
            />
          )}

          {state.step === 3 && (
            <Step3Calibration
              config={state.config}
              calibrationComplete={state.calibrationComplete}
              setCalibrationComplete={(complete) => setState(prev => ({ ...prev, calibrationComplete: complete }))}
              onNext={nextStep}
              onBack={prevStep}
            />
          )}

          {state.step === 4 && (
            <Step4Simulation
              config={state.config}
              simulationRun={state.simulationRun}
              setSimulationRun={(run) => setState(prev => ({ ...prev, simulationRun: run }))}
              onComplete={handleComplete}
              onBack={prevStep}
            />
          )}

          {state.step === 5 && (
            <SuccessState
              config={state.config as RobotConfig}
              onFinish={onComplete}
            />
          )}
        </div>
      </div>
    </div>
  );
}
