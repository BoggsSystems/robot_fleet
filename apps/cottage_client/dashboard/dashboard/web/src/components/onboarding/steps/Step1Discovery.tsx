import { useState } from 'react';
import { Wifi, Server, ChevronRight, X, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import type { RobotConfig } from '../OnboardingWizard';

interface Step1DiscoveryProps {
  config: Partial<RobotConfig>;
  updateConfig: (updates: Partial<RobotConfig>) => void;
  connectionTested: boolean;
  setConnectionTested: (tested: boolean) => void;
  onNext: () => void;
  onCancel: () => void;
}

type ConnectionStatus = 'idle' | 'testing' | 'success' | 'error';

export function Step1Discovery({
  config,
  updateConfig,
  connectionTested,
  setConnectionTested,
  onNext,
  onCancel,
}: Step1DiscoveryProps) {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>('idle');
  const [connectionError, setConnectionError] = useState('');
  const [robotInfo, setRobotInfo] = useState<{model?: string; serial?: string; firmware?: string; battery?: number}>({});

  const handleTestConnection = async () => {
    if (!config.ipAddress) return;

    setConnectionStatus('testing');
    setConnectionError('');

    try {
      const response = await fetch('/api/robots/test-connection', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ip: config.ipAddress,
          interface: config.networkInterface || 'lo0',
        }),
      });

      const data = await response.json();

      if (response.ok) {
        setConnectionStatus('success');
        setConnectionTested(true);
        setRobotInfo({
          model: data.model,
          serial: data.serial,
          firmware: data.firmware,
          battery: data.battery,
        });
        updateConfig({
          model: data.model,
          serial: data.serial,
          firmware: data.firmware,
        });
      } else {
        setConnectionStatus('error');
        setConnectionError(data.error || 'Failed to connect to robot');
        setConnectionTested(false);
      }
    } catch (err) {
      setConnectionStatus('error');
      setConnectionError('Network error. Please check your connection.');
      setConnectionTested(false);
    }
  };

  return (
    <div className="step-container">
      <h2>Step 1: Robot Discovery</h2>
      <p className="step-description">
        Connect to your Unitree robot. You can auto-discover or manually enter the IP address.
      </p>

      <div className="discovery-options">
        <label className="radio-label">
          <input type="radio" name="discovery" value="auto" defaultChecked />
          <span>Auto-discover on local network (recommended)</span>
        </label>
        <label className="radio-label">
          <input type="radio" name="discovery" value="manual" />
          <span>Manual IP entry</span>
        </label>
      </div>

      <div className="form-group">
        <label>Robot IP Address</label>
        <div className="input-with-button">
          <input
            type="text"
            placeholder="192.168.1.101"
            value={config.ipAddress || ''}
            onChange={(e) => {
              updateConfig({ ipAddress: e.target.value });
              setConnectionTested(false);
              setConnectionStatus('idle');
            }}
            className="text-input"
          />
          <button
            onClick={handleTestConnection}
            disabled={!config.ipAddress || connectionStatus === 'testing'}
            className="test-button"
          >
            {connectionStatus === 'testing' ? (
              <>
                <Loader2 className="spin" size={16} />
                Testing...
              </>
            ) : (
              <>
                <Wifi size={16} />
                Test Connection
              </>
            )}
          </button>
        </div>
      </div>

      <div className="form-group">
        <label>Network Interface</label>
        <select
          value={config.networkInterface || 'lo0'}
          onChange={(e) => updateConfig({ networkInterface: e.target.value })}
          className="select-input"
        >
          <option value="lo0">lo0 (Local/Loopback)</option>
          <option value="lo">lo (Loopback)</option>
          <option value="eth0">eth0 (Ethernet)</option>
          <option value="en0">en0 (WiFi - Mac)</option>
          <option value="enp2s0">enp2s0 (Ethernet - Linux)</option>
        </select>
        <span className="input-help">
          Select the network card connected to robot LAN
        </span>
      </div>

      {connectionStatus === 'success' && (
        <div className="success-panel">
          <div className="success-header">
            <CheckCircle className="success-icon" size={24} />
            <span>Connection Successful!</span>
          </div>
          <div className="robot-info-grid">
            <div className="info-item">
              <Server size={16} />
              <span>Model: {robotInfo.model}</span>
            </div>
            <div className="info-item">
              <span className="label">Serial:</span>
              <span>{robotInfo.serial}</span>
            </div>
            <div className="info-item">
              <span className="label">Firmware:</span>
              <span>{robotInfo.firmware}</span>
            </div>
            <div className="info-item">
              <span className="label">Battery:</span>
              <span className="battery-level">{robotInfo.battery}%</span>
            </div>
          </div>
        </div>
      )}

      {connectionStatus === 'error' && (
        <div className="error-panel">
          <div className="error-header">
            <AlertCircle className="error-icon" size={24} />
            <span>Connection Failed</span>
          </div>
          <p>{connectionError}</p>
          <div className="troubleshooting">
            <strong>Troubleshooting:</strong>
            <ul>
              <li>Verify robot is powered on (check LCD on back panel)</li>
              <li>Check network cable/WiFi connection</li>
              <li>Verify IP address matches robot display</li>
              <li>Ensure firewall allows DDS traffic (ports 7400-7450)</li>
            </ul>
          </div>
        </div>
      )}

      <div className="step-actions">
        <button onClick={onCancel} className="btn-secondary">
          <X size={16} />
          Cancel
        </button>
        <button
          onClick={onNext}
          disabled={!connectionTested}
          className="btn-primary"
        >
          Continue
          <ChevronRight size={16} />
        </button>
      </div>

      <div className="step-tip">
        💡 <strong>Tip:</strong> You can find the robot's IP on the LCD display on the robot's back panel when powered on
      </div>
    </div>
  );
}
