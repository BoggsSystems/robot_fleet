import { useState } from 'react';
import { ChevronRight, ChevronLeft, User, MapPin, Briefcase, Layers, Bot } from 'lucide-react';
import type { RobotConfig } from '../OnboardingWizard';

interface Step2IdentityProps {
  config: Partial<RobotConfig>;
  updateConfig: (updates: Partial<RobotConfig>) => void;
  existingRobots: string[];
  onNext: () => void;
  onBack: () => void;
}

const ZONES = [
  { id: 'main_warehouse', name: 'Main Warehouse', subZones: ['Aisle A-C', 'Aisle D-F', 'Aisle G-I'] },
  { id: 'receiving', name: 'Receiving Dock', subZones: ['Dock 1-2', 'Dock 3-4'] },
  { id: 'shipping', name: 'Shipping Area', subZones: ['Outbound A', 'Outbound B'] },
  { id: 'storage', name: 'Cold Storage', subZones: ['Freezer', 'Cooler'] },
];

const ROBOT_TYPES = [
  {
    id: 'unitree_r1',
    name: 'Unitree R1',
    category: 'Humanoid',
    icon: '🤖',
    description: 'Full-size humanoid for complex manipulation tasks',
    capabilities: ['walk', 'manipulate', 'climb_stairs', 'carry_load'],
    sdk: 'unitree_sdk2'
  },
  {
    id: 'unitree_g1',
    name: 'Unitree G1',
    category: 'Humanoid',
    icon: '🤖',
    description: 'Compact humanoid for agile operations',
    capabilities: ['walk', 'manipulate', 'climb_stairs'],
    sdk: 'unitree_sdk2'
  },
  {
    id: 'unitree_go2',
    name: 'Unitree Go2',
    category: 'Quadruped',
    icon: '🐕',
    description: 'Fast quadruped for traversal and patrol',
    capabilities: ['walk', 'run', 'climb_stairs', 'rough_terrain'],
    sdk: 'unitree_sdk2'
  },
  {
    id: 'generic_mobile',
    name: 'Generic Mobile Robot',
    category: 'Wheeled',
    icon: '🔄',
    description: 'Standard wheeled platform for flat surfaces',
    capabilities: ['walk', 'carry_load'],
    sdk: 'ros2'
  },
  {
    id: 'custom',
    name: 'Custom / Other',
    category: 'Custom',
    icon: '⚙️',
    description: 'Custom robot with manual configuration',
    capabilities: [],
    sdk: 'custom'
  }
];
const CAPABILITIES = [
  { id: 'inventory_scan', name: 'Inventory Scanning', icon: '🔍' },
  { id: 'restock', name: 'Restocking', icon: '📦' },
  { id: 'pick_place', name: 'Pick & Place', icon: '🏭' },
  { id: 'sanitation', name: 'Sanitation', icon: '🧹' },
  { id: 'inspection', name: 'Quality Inspection', icon: '✓' },
  { id: 'patrol', name: 'Security Patrol', icon: '👁' },
];

export function Step2Identity({
  config,
  updateConfig,
  existingRobots,
  onNext,
  onBack,
}: Step2IdentityProps) {
  const [selectedZone, setSelectedZone] = useState(config.zone || '');
  const [selectedType, setSelectedType] = useState(config.robotType || '');
  const [nameError, setNameError] = useState('');
  const [idError, setIdError] = useState('');

  const validateAndProceed = () => {
    let valid = true;
    
    if (!config.name || config.name.length < 3) {
      setNameError('Name must be at least 3 characters');
      valid = false;
    } else {
      setNameError('');
    }

    if (!config.robotId || config.robotId.length < 3) {
      setIdError('Robot ID must be at least 3 characters');
      valid = false;
    } else if (existingRobots.includes(config.robotId)) {
      setIdError('Robot ID already exists');
      valid = false;
    } else {
      setIdError('');
    }

    if (!selectedType) {
      valid = false;
    }

    if (valid && selectedZone && selectedType) {
      const robotType = ROBOT_TYPES.find(t => t.id === selectedType);
      if (robotType) {
        updateConfig({ 
          zone: selectedZone,
          robotType: selectedType,
          robotCategory: robotType.category,
          vendor: robotType.sdk,
          // Auto-populate capabilities based on robot type
          capabilities: robotType.capabilities || config.capabilities || []
        });
      }
      onNext();
    }
  };

  const generateRobotId = (name: string, type: string) => {
    const base = name.toLowerCase().replace(/[^a-z0-9]/g, '_');
    const typePrefix = type ? type.split('_')[0] : 'bot';
    return `${typePrefix}_${base}`;
  };

  const handleTypeSelect = (typeId: string) => {
    setSelectedType(typeId);
    const robotType = ROBOT_TYPES.find(t => t.id === typeId);
    if (robotType && config.name && !config.robotId) {
      updateConfig({ 
        robotId: generateRobotId(config.name, typeId),
        robotType: typeId,
        robotCategory: robotType.category,
        vendor: robotType.sdk
      });
    }
  };

  return (
    <div className="step-container">
      <h2>Step 2: Robot Identity</h2>
      <p className="step-description">
        Select your robot type and configure its identity for the fleet.
      </p>

      {/* Robot Type Selection */}
      <div className="form-section">
        <label className="section-label">
          <Bot size={16} />
          Robot Type
        </label>
        <div className="robot-type-grid">
          {ROBOT_TYPES.map((type) => (
            <div
              key={type.id}
              className={`robot-type-card ${selectedType === type.id ? 'selected' : ''}`}
              onClick={() => handleTypeSelect(type.id)}
            >
              <div className="robot-type-header">
                <span className="robot-type-icon">{type.icon}</span>
                <span className="robot-category">{type.category}</span>
              </div>
              <h4>{type.name}</h4>
              <p>{type.description}</p>
              <div className="robot-type-meta">
                <span className="sdk-badge">{type.sdk}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="form-section">
        <div className="form-group">
          <label>
            <User size={16} />
            Robot Name
          </label>
          <input
            type="text"
            placeholder="e.g., Warehouse-Bot-01"
            value={config.name || ''}
            onChange={(e) => {
              const name = e.target.value;
              updateConfig({ 
                name,
                robotId: config.robotId || generateRobotId(name, selectedType),
              });
              setNameError('');
            }}
            className="text-input"
          />
          {nameError && <span className="error-text">{nameError}</span>}
        </div>

        <div className="form-group">
          <label>
            <Layers size={16} />
            Robot ID
          </label>
          <input
            type="text"
            placeholder="r1_warehouse_bot_01"
            value={config.robotId || ''}
            onChange={(e) => {
              updateConfig({ robotId: e.target.value });
              setIdError('');
            }}
            className="text-input"
          />
          <span className="input-help">Used in logs and API calls (lowercase, no spaces)</span>
          {idError && <span className="error-text">{idError}</span>}
        </div>
      </div>

      <div className="form-section">
        <label className="section-label">
          <MapPin size={16} />
          Work Zone Assignment
        </label>
        <div className="zone-grid">
          {ZONES.map((zone) => (
            <div
              key={zone.id}
              className={`zone-card ${selectedZone === zone.id ? 'selected' : ''}`}
              onClick={() => setSelectedZone(zone.id)}
            >
              <h4>{zone.name}</h4>
              <select
                disabled={selectedZone !== zone.id}
                value={config.subZone || ''}
                onChange={(e) => updateConfig({ subZone: e.target.value })}
                onClick={(e) => e.stopPropagation()}
              >
                <option value="">Select sub-zone...</option>
                {zone.subZones.map((sub) => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>
          ))}
        </div>
      </div>

      <div className="form-section">
        <label className="section-label">
          <Briefcase size={16} />
          Assign Capabilities
        </label>
        <div className="capabilities-grid">
          {CAPABILITIES.map((cap) => (
            <label
              key={cap.id}
              className={`capability-card ${config.capabilities?.includes(cap.id) ? 'selected' : ''}`}
            >
              <input
                type="checkbox"
                checked={config.capabilities?.includes(cap.id) || false}
                onChange={(e) => {
                  const current = config.capabilities || [];
                  if (e.target.checked) {
                    updateConfig({ capabilities: [...current, cap.id] });
                  } else {
                    updateConfig({ capabilities: current.filter((c) => c !== cap.id) });
                  }
                }}
              />
              <span className="capability-icon">{cap.icon}</span>
              <span className="capability-name">{cap.name}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="step-actions">
        <button onClick={onBack} className="btn-secondary">
          <ChevronLeft size={16} />
          Back
        </button>
        <button 
          onClick={validateAndProceed} 
          className="btn-primary"
          disabled={!config.name || !config.robotId || !selectedZone || !selectedType}
        >
          Continue
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  );
}
