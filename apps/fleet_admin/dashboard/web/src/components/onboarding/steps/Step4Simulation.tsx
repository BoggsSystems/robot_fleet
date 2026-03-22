import { useState } from 'react';
import { ChevronRight, ChevronLeft, Play, CheckCircle, Gamepad2, Zap, Shield } from 'lucide-react';
import type { RobotConfig } from '../OnboardingWizard';

interface Step4SimulationProps {
  config: Partial<RobotConfig>;
  simulationRun: boolean;
  setSimulationRun: (run: boolean) => void;
  onComplete: () => void;
  onBack: () => void;
}

type SimScenario = 'basic' | 'warehouse' | 'emergency' | 'battery';

interface Scenario {
  id: SimScenario;
  name: string;
  description: string;
  duration: string;
  icon: React.ReactNode;
}

const SCENARIOS: Scenario[] = [
  {
    id: 'basic',
    name: 'Basic Navigation',
    description: 'Walk 2m, turn 90°, verify stability',
    duration: '1 min',
    icon: <Zap size={20} />,
  },
  {
    id: 'warehouse',
    name: 'Warehouse Simulation',
    description: 'Navigate around shelves, avoid obstacles',
    duration: '3 min',
    icon: <Gamepad2 size={20} />,
  },
  {
    id: 'emergency',
    name: 'Emergency Stop Test',
    description: 'Test emergency stop and recovery',
    duration: '2 min',
    icon: <Shield size={20} />,
  },
  {
    id: 'battery',
    name: 'Battery Drain Simulation',
    description: 'Simulate low-battery behavior',
    duration: '5 min',
    icon: <Zap size={20} />,
  },
];

export function Step4Simulation({
  config,
  simulationRun,
  setSimulationRun,
  onComplete,
  onBack,
}: Step4SimulationProps) {
  const [selectedScenario, setSelectedScenario] = useState<SimScenario>('warehouse');
  const [simStatus, setSimStatus] = useState<'idle' | 'running' | 'complete'>('idle');
  const [simResults, setSimResults] = useState<{success: boolean; message: string} | null>(null);

  const runSimulation = async () => {
    setSimStatus('running');
    setSimulationRun(true);

    try {
      const response = await fetch('/api/robots/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          robotId: config.robotId,
          scenario: selectedScenario,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setSimStatus('complete');
        setSimResults({ success: true, message: data.message });
      } else {
        setSimStatus('idle');
        setSimResults({ success: false, message: data.error });
      }
    } catch (err) {
      setSimStatus('idle');
      setSimResults({ success: false, message: 'Simulation failed to start' });
    }
  };

  return (
    <div className="step-container">
      <h2>Step 4: Virtual Training</h2>
      <p className="step-description">
        Run your robot through a virtual MuJoCo simulation before deploying to the physical workspace.
      </p>

      <div className="sim-container">
        <div className="sim-header">
          <Gamepad2 size={24} />
          <span>MuJoCo Simulator</span>
        </div>

        <div className="scenario-grid">
          {SCENARIOS.map((scenario) => (
            <div
              key={scenario.id}
              className={`scenario-card ${selectedScenario === scenario.id ? 'selected' : ''}`}
              onClick={() => setSelectedScenario(scenario.id)}
            >
              <div className="scenario-icon">{scenario.icon}</div>
              <h4>{scenario.name}</h4>
              <p>{scenario.description}</p>
              <span className="scenario-duration">{scenario.duration}</span>
            </div>
          ))}
        </div>

        <div className="sim-status-panel">
          {simStatus === 'idle' && (
            <div className="sim-ready">
              <p>Ready to launch simulation</p>
              <button onClick={runSimulation} className="sim-launch-button">
                <Play size={16} />
                Launch Simulation
              </button>
            </div>
          )}

          {simStatus === 'running' && (
            <div className="sim-running">
              <div className="sim-spinner"></div>
              <p>Running simulation...</p>
              <span className="sim-eta">ETA: {SCENARIOS.find(s => s.id === selectedScenario)?.duration}</span>
            </div>
          )}

          {simStatus === 'complete' && simResults && (
            <div className={`sim-complete ${simResults.success ? 'success' : 'error'}`}>
              <CheckCircle size={24} />
              <p>{simResults.message}</p>
              <button onClick={() => setSimStatus('idle')} className="sim-retry-button">
                Run Again
              </button>
            </div>
          )}
        </div>

        <div className="sim-preview">
          <div className="preview-placeholder">
            <Gamepad2 size={48} />
            <p>3D simulation preview will appear here</p>
            <span>Powered by MuJoCo</span>
          </div>
        </div>
      </div>

      <div className="step-actions">
        <button onClick={onBack} className="btn-secondary">
          <ChevronLeft size={16} />
          Back
        </button>
        <div className="action-group">
          <button onClick={onComplete} className="btn-secondary skip">
            Skip Simulation
          </button>
          <button 
            onClick={onComplete} 
            className="btn-primary"
          >
            {simulationRun ? (
              <>
                <CheckCircle size={16} />
                Complete Onboarding
              </>
            ) : (
              <>
                Complete
                <ChevronRight size={16} />
              </>
            )}
          </button>
        </div>
      </div>

      <div className="step-tip">
        💡 <strong>Tip:</strong> Simulating first is recommended for new robots to verify behavior before physical deployment
      </div>
    </div>
  );
}
