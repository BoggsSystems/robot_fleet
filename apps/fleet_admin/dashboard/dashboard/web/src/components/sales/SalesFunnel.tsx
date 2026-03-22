import { useState, useMemo } from 'react';
import { ArrowRight, Bot, Building2, CheckCircle, Sparkles, Zap } from 'lucide-react';
import { RobotImage } from '../ui/RobotImage';
import './SalesFunnel.css';

export type FunnelStage = 
  | 'landing'
  | 'demo_booking'
  | 'simulation'
  | 'proposal'
  | 'contract'
  | 'deployment'
  | 'complete';

export type LeadData = {
  id: string;
  companyName: string;
  contactName: string;
  email: string;
  phone: string;
  industry: string;
  facilitySize: string;
  useCase: string;
  estimatedRobots: number;
  timeline: string;
  budget: string;
  createdAt: string;
  currentStage: FunnelStage;
  notes: string[];
};

interface SalesFunnelProps {
  onComplete?: (lead: LeadData) => void;
  initialStage?: FunnelStage;
  initialData?: Partial<LeadData>;
}

const DEFAULT_LEAD: Partial<LeadData> = {
  companyName: 'TechCorp Industries',
  contactName: 'Sarah Mitchell',
  email: 's.mitchell@techcorp.com',
  phone: '+1 (555) 987-2345',
  industry: 'manufacturing',
  facilitySize: '50000-100000',
  useCase: 'automated_material_handling',
  estimatedRobots: 5,
  timeline: '3-6_months',
  budget: '100k-250k',
  notes: ['Referred by existing client', 'Interested in R1 and Go2 mix'],
};

const INDUSTRIES = [
  { id: 'manufacturing', name: 'Manufacturing', icon: '🏭' },
  { id: 'warehousing', name: 'Warehousing & Logistics', icon: '📦' },
  { id: 'retail', name: 'Retail & E-commerce', icon: '🛒' },
  { id: 'healthcare', name: 'Healthcare', icon: '🏥' },
  { id: 'hospitality', name: 'Hospitality', icon: '🏨' },
  { id: 'office', name: 'Corporate Office', icon: '🏢' },
];

const USE_CASES = [
  { id: 'automated_material_handling', name: 'Automated Material Handling', desc: 'Move inventory, restock shelves, transport goods' },
  { id: 'security_patrol', name: 'Security & Patrol', desc: '24/7 facility monitoring, anomaly detection' },
  { id: 'quality_inspection', name: 'Quality Inspection', desc: 'Visual inspection, defect detection, compliance checks' },
  { id: 'customer_service', name: 'Customer Service', desc: 'Guidance, information, assistance in public spaces' },
  { id: 'cleaning_maintenance', name: 'Cleaning & Maintenance', desc: 'Facility cleaning, maintenance tasks' },
  { id: 'research_assistant', name: 'Research & Lab Assistant', desc: 'Lab work, sample transport, data collection' },
];

export function SalesFunnel({ onComplete, initialStage = 'landing', initialData }: SalesFunnelProps) {
  const [stage, setStage] = useState<FunnelStage>(initialStage);
  const [leadData, setLeadData] = useState<Partial<LeadData>>(initialData || DEFAULT_LEAD);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Generate stable IDs that don't change on every render
  const proposalId = useMemo(() => 
    Math.random().toString(36).substr(2, 9).toUpperCase(), 
    []
  );
  const contractId = useMemo(() => 
    Math.random().toString(36).substr(2, 6).toUpperCase(), 
    []
  );

  const updateLead = (updates: Partial<LeadData>) => {
    setLeadData(prev => ({ ...prev, ...updates }));
  };

  const handleNext = (nextStage: FunnelStage) => {
    setIsSubmitting(true);
    setTimeout(() => {
      setStage(nextStage);
      setIsSubmitting(false);
    }, 600);
  };

  const renderLanding = () => (
    <div className="funnel-landing">
      <div className="landing-hero">
        <div className="hero-badge">
          <Sparkles size={14} />
          <span>Unitree-Powered Automation</span>
        </div>
        <h1>Transform Your Operations with Real Robots</h1>
        <p className="hero-subtitle">
          Deploy cutting-edge Unitree R1 humanoid and Go2 quadruped robots. 
          From simulation to live deployment in 60 days.
        </p>
        
        {/* PROMINENT ROBOT SHOWCASE */}
        <div className="hero-robots">
          <div className="robot-showcase">
            <div className="robot-card r1-robot">
              <div className="robot-image featured">
                <RobotImage 
                  src="/images/robots/r1-hero.png" 
                  alt="Unitree R1 Humanoid Robot - 1.22m tall humanoid robot standing upright"
                  className="r1-image"
                  loading="eager"
                />
                <div className="robot-badge">HUMANOID</div>
              </div>
              <div className="robot-info">
                <h3>R1 Humanoid Robot</h3>
                <p className="robot-description">
                  <strong>1.22m tall humanoid</strong> with 26-DOF for complex manipulation tasks
                </p>
                <div className="robot-specs">
                  <span className="spec-primary">🤖 Humanoid</span>
                  <span>1.22m height</span>
                  <span>25kg weight</span>
                  <span>$5,900+</span>
                </div>
                <div className="robot-features">
                  <div className="feature">✓ 20-26 DOF Movement</div>
                  <div className="feature">✓ Voice & Vision AI</div>
                  <div className="feature">✓ Fully Customizable</div>
                </div>
              </div>
            </div>
            
            <div className="robot-card go2-robot">
              <div className="robot-image featured">
                <RobotImage 
                  src="/images/robots/go2-hero.png" 
                  alt="Unitree Go2 Quadruped Robot - Four-legged robot dog with 4D LiDAR"
                  className="go2-image"
                  loading="eager"
                />
                <div className="robot-badge">QUADRUPED</div>
              </div>
              <div className="robot-info">
                <h3>Go2 Robot Dog</h3>
                <p className="robot-description">
                  <strong>Four-legged robot</strong> with 4D LiDAR and advanced AI capabilities
                </p>
                <div className="robot-specs">
                  <span className="spec-primary">🐕 Quadruped</span>
                  <span>15kg weight</span>
                  <span>2.5m/s speed</span>
                  <span>8000mAh battery</span>
                </div>
                <div className="robot-features">
                  <div className="feature">✓ 4D Ultra-Wide LiDAR</div>
                  <div className="feature">✓ AI-Powered Navigation</div>
                  <div className="feature">✓ All-Terrain Capability</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div className="hero-stats">
          <div className="stat">
            <span className="stat-number">40%</span>
            <span className="stat-label">Cost Reduction</span>
          </div>
          <div className="stat">
            <span className="stat-number">3x</span>
            <span className="stat-label">Productivity Gain</span>
          </div>
          <div className="stat">
            <span className="stat-number">24/7</span>
            <span className="stat-label">Operation</span>
          </div>
        </div>
      </div>

      <div className="lead-form-container">
        <div className="form-header">
          <h2>Get Your Free Simulation</h2>
          <p>See how robots would work in your facility - no commitment required</p>
        </div>

        <div className="lead-form">
          <div className="form-row">
            <div className="form-field">
              <label>Company Name</label>
              <input
                type="text"
                value={leadData.companyName}
                onChange={(e) => updateLead({ companyName: e.target.value })}
                placeholder="Acme Corporation"
              />
            </div>
            <div className="form-field">
              <label>Your Name</label>
              <input
                type="text"
                value={leadData.contactName}
                onChange={(e) => updateLead({ contactName: e.target.value })}
                placeholder="John Smith"
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Email</label>
              <input
                type="email"
                value={leadData.email}
                onChange={(e) => updateLead({ email: e.target.value })}
                placeholder="john@company.com"
              />
            </div>
            <div className="form-field">
              <label>Phone</label>
              <input
                type="tel"
                value={leadData.phone}
                onChange={(e) => updateLead({ phone: e.target.value })}
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          <div className="form-field">
            <label>Industry</label>
            <div className="option-grid">
              {INDUSTRIES.map(ind => (
                <button
                  key={ind.id}
                  className={`option-card ${leadData.industry === ind.id ? 'selected' : ''}`}
                  onClick={() => updateLead({ industry: ind.id })}
                >
                  <span className="option-icon">{ind.icon}</span>
                  <span className="option-name">{ind.name}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="form-field">
            <label>What do you need robots to do?</label>
            <div className="use-case-list">
              {USE_CASES.map(useCase => (
                <button
                  key={useCase.id}
                  className={`use-case-card ${leadData.useCase === useCase.id ? 'selected' : ''}`}
                  onClick={() => updateLead({ useCase: useCase.id })}
                >
                  <div className="use-case-header">
                    <span className="use-case-name">{useCase.name}</span>
                    {leadData.useCase === useCase.id && <CheckCircle size={16} className="check-icon" />}
                  </div>
                  <span className="use-case-desc">{useCase.desc}</span>
                </button>
              ))}
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Facility Size</label>
              <select
                value={leadData.facilitySize}
                onChange={(e) => updateLead({ facilitySize: e.target.value })}
              >
                <option value="10000-25000">10,000 - 25,000 sq ft</option>
                <option value="25000-50000">25,000 - 50,000 sq ft</option>
                <option value="50000-100000">50,000 - 100,000 sq ft</option>
                <option value="100000+">100,000+ sq ft</option>
              </select>
            </div>
            <div className="form-field">
              <label>Timeline</label>
              <select
                value={leadData.timeline}
                onChange={(e) => updateLead({ timeline: e.target.value })}
              >
                <option value="immediate">Immediate (ASAP)</option>
                <option value="1-3_months">1-3 months</option>
                <option value="3-6_months">3-6 months</option>
                <option value="6-12_months">6-12 months</option>
                <option value="exploring">Just exploring</option>
              </select>
            </div>
          </div>

          <div className="form-row">
            <div className="form-field">
              <label>Estimated Robot Fleet Size</label>
              <div className="robot-counter">
                <button 
                  className="counter-btn"
                  onClick={() => updateLead({ estimatedRobots: Math.max(1, (leadData.estimatedRobots || 1) - 1) })}
                >-</button>
                <div className="counter-value">
                  <Bot size={20} />
                  <span>{leadData.estimatedRobots || 1}</span>
                </div>
                <button 
                  className="counter-btn"
                  onClick={() => updateLead({ estimatedRobots: (leadData.estimatedRobots || 1) + 1 })}
                >+</button>
              </div>
            </div>
            <div className="form-field">
              <label>Budget Range</label>
              <select
                value={leadData.budget}
                onChange={(e) => updateLead({ budget: e.target.value })}
              >
                <option value="50k-100k">$50K - $100K</option>
                <option value="100k-250k">$100K - $250K</option>
                <option value="250k-500k">$250K - $500K</option>
                <option value="500k+">$500K+</option>
              </select>
            </div>
          </div>

          <button 
            className="btn-funnel-next"
            onClick={() => handleNext('demo_booking')}
            disabled={isSubmitting}
          >
            {isSubmitting ? (
              <><span className="spinner-small" /> Processing...</>
            ) : (
              <>See Your Simulation <ArrowRight size={18} /></>
            )}
          </button>

          <p className="form-disclaimer">
            No commitment required. Our team will prepare a custom simulation based on your facility.
          </p>
        </div>
      </div>
    </div>
  );

  const renderDemoBooking = () => (
    <div className="funnel-stage">
      <div className="stage-header">
        <h2>Schedule Your Demo</h2>
        <p>Choose a time to see your custom simulation</p>
      </div>

      <div className="demo-preview">
        <div className="preview-card">
          <div className="preview-header">
            <Building2 size={20} />
            <span>Your Facility Simulation</span>
          </div>
          <div className="preview-content">
            <div className="facility-stats">
              <div className="stat-row">
                <span>Company</span>
                <strong>{leadData.companyName}</strong>
              </div>
              <div className="stat-row">
                <span>Industry</span>
                <strong>{INDUSTRIES.find(i => i.id === leadData.industry)?.name}</strong>
              </div>
              <div className="stat-row">
                <span>Use Case</span>
                <strong>{USE_CASES.find(u => u.id === leadData.useCase)?.name}</strong>
              </div>
              <div className="stat-row">
                <span>Est. Fleet</span>
                <strong>{leadData.estimatedRobots} robots</strong>
              </div>
            </div>
          </div>
        </div>

        <div className="simulation-preview">
          <h3>Preview: {leadData.estimatedRobots} Robot Configuration</h3>
          <div className="sim-grid">
            {Array.from({ length: Math.min(leadData.estimatedRobots || 3, 6) }).map((_, i) => (
              <div key={i} className="sim-robot">
                <Bot size={32} />
                <span>Unitree {i % 2 === 0 ? 'R1' : 'Go2'}</span>
              </div>
            ))}
          </div>
          <div className="sim-metrics">
            <div className="sim-metric">
              <span className="metric-label">Projected Efficiency</span>
              <span className="metric-value">+140%</span>
            </div>
            <div className="sim-metric">
              <span className="metric-label">Monthly Savings</span>
              <span className="metric-value">$12,400</span>
            </div>
            <div className="sim-metric">
              <span className="metric-label">ROI Timeline</span>
              <span className="metric-value">8 months</span>
            </div>
          </div>
        </div>
      </div>

      <div className="booking-slots">
        <h3>Available Demo Times</h3>
        <div className="slot-grid">
          {['Today 2:00 PM', 'Today 4:00 PM', 'Tomorrow 10:00 AM', 'Tomorrow 2:00 PM', 'Thu 11:00 AM', 'Fri 3:00 PM'].map((slot, i) => (
            <button key={i} className={`slot-btn ${i === 2 ? 'selected' : ''}`}>
              <Zap size={14} />
              {slot}
            </button>
          ))}
        </div>
      </div>

      <div className="funnel-actions">
        <button className="btn-secondary" onClick={() => setStage('landing')}>
          Back
        </button>
        <button className="btn-funnel-next" onClick={() => handleNext('simulation')}>
          Confirm Demo <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderSimulation = () => (
    <div className="funnel-stage">
      <div className="stage-header">
        <h2>Live Simulation</h2>
        <p>Watch your robots in action (simulated environment)</p>
      </div>

      <div className="simulation-viewer">
        <div className="sim-canvas">
          <div className="sim-facility">
            <div className="facility-label">{leadData.companyName} - Facility Layout</div>
            <div className="sim-robots-active">
              {Array.from({ length: leadData.estimatedRobots || 3 }).map((_, i) => (
                <div 
                  key={i} 
                  className="sim-robot-dot"
                  style={{
                    animationDelay: `${i * 0.5}s`,
                    left: `${20 + (i * 15)}%`,
                    top: `${30 + (i % 2) * 20}%`,
                  }}
                >
                  <Bot size={20} />
                </div>
              ))}
            </div>
            <div className="sim-paths">
              <svg className="path-svg" viewBox="0 0 100 100" preserveAspectRatio="none">
                <path d="M20,30 Q50,20 80,40 T20,70" className="path-line" />
                <path d="M30,50 Q60,40 70,60 T40,80" className="path-line" style={{ animationDelay: '0.5s' }} />
              </svg>
            </div>
          </div>
        </div>

        <div className="sim-controls">
          <div className="control-panel">
            <h4>Simulation Controls</h4>
            <div className="control-buttons">
              <button className="control-btn active">▶ Play</button>
              <button className="control-btn">⏸ Pause</button>
              <button className="control-btn">↻ Reset</button>
            </div>
            <div className="sim-speed">
              <label>Speed</label>
              <input type="range" min="0.5" max="3" step="0.5" defaultValue="1" />
            </div>
          </div>

          <div className="live-metrics">
            <h4>Live Metrics</h4>
            <div className="metric-row">
              <span>Tasks Completed</span>
              <strong>147</strong>
            </div>
            <div className="metric-row">
              <span>Avg Task Time</span>
              <strong>2.3 min</strong>
            </div>
            <div className="metric-row">
              <span>Distance Covered</span>
              <strong>4.2 km</strong>
            </div>
            <div className="metric-row">
              <span>Battery Status</span>
              <strong className="status-good">Optimal</strong>
            </div>
          </div>
        </div>
      </div>

      <div className="simulation-summary">
        <div className="summary-card recommended">
          <div className="summary-header">
            <CheckCircle size={20} />
            <span>Recommended Configuration</span>
          </div>
          <div className="summary-content">
            <div className="robot-recommendation">
              <div className="rec-item">
                <Bot size={24} />
                <div>
                  <strong>3× Unitree R1</strong>
                  <span>Heavy lifting & manipulation</span>
                </div>
              </div>
              <div className="rec-item">
                <Bot size={24} />
                <div>
                  <strong>2× Unitree Go2</strong>
                  <span>Fast transport & patrol</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="funnel-actions">
        <button className="btn-secondary" onClick={() => setStage('demo_booking')}>
          Back
        </button>
        <button className="btn-funnel-next" onClick={() => handleNext('proposal')}>
          Get Your Quote <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderProposal = () => (
    <div className="funnel-stage">
      <div className="stage-header">
        <h2>Your Custom Proposal</h2>
        <p>RFaaS Package tailored for {leadData.companyName}</p>
      </div>

      <div className="proposal-document">
        <div className="proposal-header">
          <div className="proposal-logo">🤖</div>
          <div className="proposal-meta">
            <h3>Robot Fleet as a Service</h3>
            <span>Proposal #{proposalId}</span>
            <span className="proposal-date">{new Date().toLocaleDateString()}</span>
          </div>
        </div>

        <div className="proposal-section">
          <h4>Fleet Configuration</h4>
          <div className="fleet-breakdown">
            <div className="fleet-item">
              <div className="fleet-icon">🤖</div>
              <div className="fleet-details">
                <strong>Unitree R1 Humanoid × 3</strong>
                <span>Complex manipulation tasks</span>
              </div>
              <div className="fleet-price">$3,600/mo</div>
            </div>
            <div className="fleet-item">
              <div className="fleet-icon">🐕</div>
              <div className="fleet-details">
                <strong>Unitree Go2 Quadruped × 2</strong>
                <span>Transport & patrol</span>
              </div>
              <div className="fleet-price">$2,400/mo</div>
            </div>
          </div>
        </div>

        <div className="proposal-section">
          <h4>Service Inclusions</h4>
          <div className="service-list">
            {['Hardware & Software', '24/7 Remote Monitoring', 'Preventive Maintenance', 'Software Updates', 'Priority Support', 'Performance Analytics'].map((service, i) => (
              <div key={i} className="service-item">
                <CheckCircle size={14} className="service-check" />
                <span>{service}</span>
              </div>
            ))}
          </div>
        </div>

        <div className="proposal-totals">
          <div className="total-row">
            <span>Monthly Subscription</span>
            <strong>$6,000/mo</strong>
          </div>
          <div className="total-row">
            <span>Setup & Provisioning</span>
            <strong>$15,000 (one-time)</strong>
          </div>
          <div className="total-row highlight">
            <span>First Year Total</span>
            <strong>$87,000</strong>
          </div>
          <div className="savings-highlight">
            <span>💡 Compared to hiring: Save $156,000/year</span>
          </div>
        </div>
      </div>

      <div className="proposal-options">
        <div className="option-toggle">
          <label>Contract Length</label>
          <div className="toggle-group">
            <button className="toggle-btn">12 months</button>
            <button className="toggle-btn active">24 months (10% off)</button>
            <button className="toggle-btn">36 months (15% off)</button>
          </div>
        </div>
      </div>

      <div className="funnel-actions">
        <button className="btn-secondary" onClick={() => setStage('simulation')}>
          Back
        </button>
        <button className="btn-funnel-next" onClick={() => handleNext('contract')}>
          Accept Proposal <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderContract = () => (
    <div className="funnel-stage">
      <div className="stage-header">
        <h2>Service Agreement</h2>
        <p>Review and sign your RFaaS contract</p>
      </div>

      <div className="contract-document">
        <div className="contract-header">
          <h3>Robot Fleet as a Service Agreement</h3>
          <span>Contract #RF-2024-{contractId}</span>
        </div>

        <div className="contract-parties">
          <div className="party">
            <strong>Provider</strong>
            <span>Robot Fleet Solutions, Inc.</span>
          </div>
          <div className="party">
            <strong>Client</strong>
            <span>{leadData.companyName}</span>
            <span>{leadData.contactName}</span>
          </div>
        </div>

        <div className="contract-clauses">
          <div className="clause">
            <h4>1. Service Description</h4>
            <p>Provider will deliver, install, and manage {leadData.estimatedRobots} Unitree robots for automated material handling at Client's facility.</p>
          </div>
          <div className="clause">
            <h4>2. Term & Payment</h4>
            <p>24-month commitment. Monthly fee: $6,000. Setup fee: $15,000 due upon execution.</p>
          </div>
          <div className="clause">
            <h4>3. Service Level Agreement</h4>
            <p>99.5% uptime guarantee. 4-hour response time for critical issues. 24/7 remote monitoring included.</p>
          </div>
          <div className="clause">
            <h4>4. Equipment & Maintenance</h4>
            <p>All hardware remains property of Provider. Preventive maintenance, repairs, and software updates included.</p>
          </div>
        </div>

        <div className="contract-signature">
          <div className="signature-block">
            <label>Authorized Signature</label>
            <div className="signature-pad">
              <span className="signature-placeholder">Click to sign</span>
            </div>
            <input type="text" placeholder="Type your full name" defaultValue={leadData.contactName} />
          </div>
          <div className="signature-date">
            <label>Date</label>
            <input type="date" defaultValue={new Date().toISOString().split('T')[0]} />
          </div>
        </div>
      </div>

      <div className="funnel-actions">
        <button className="btn-secondary" onClick={() => setStage('proposal')}>
          Back
        </button>
        <button className="btn-funnel-next" onClick={() => handleNext('deployment')}>
          Sign & Continue <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderDeployment = () => (
    <div className="funnel-stage">
      <div className="stage-header">
        <h2>Deployment Schedule</h2>
        <p>Plan your robot fleet arrival and installation</p>
      </div>

      <div className="deployment-timeline">
        <div className="timeline-item complete">
          <div className="timeline-marker">
            <CheckCircle size={16} />
          </div>
          <div className="timeline-content">
            <strong>Contract Signed</strong>
            <span>Today - {new Date().toLocaleDateString()}</span>
          </div>
        </div>

        <div className="timeline-item active">
          <div className="timeline-marker">2</div>
          <div className="timeline-content">
            <strong>Facility Assessment</strong>
            <span>Week 1 - Site survey & preparation</span>
          </div>
        </div>

        <div className="timeline-item">
          <div className="timeline-marker">3</div>
          <div className="timeline-content">
            <strong>Robot Provisioning</strong>
            <span>Week 2-3 - Configuration & testing</span>
          </div>
        </div>

        <div className="timeline-item">
          <div className="timeline-marker">4</div>
          <div className="timeline-content">
            <strong>Delivery & Installation</strong>
            <span>Week 4 - On-site deployment</span>
          </div>
        </div>

        <div className="timeline-item">
          <div className="timeline-marker">5</div>
          <div className="timeline-content">
            <strong>Training & Go-Live</strong>
            <span>Week 5 - Staff training & launch</span>
          </div>
        </div>
      </div>

      <div className="deployment-form">
        <div className="form-section">
          <h4>Delivery Details</h4>
          <div className="form-row">
            <div className="form-field">
              <label>Shipping Address</label>
              <input type="text" placeholder="Enter facility address" defaultValue="1234 Industrial Parkway, Building C" />
            </div>
          </div>
          <div className="form-row">
            <div className="form-field">
              <label>Preferred Delivery Date</label>
              <input type="date" defaultValue={new Date(Date.now() + 28 * 24 * 60 * 60 * 1000).toISOString().split('T')[0]} />
            </div>
            <div className="form-field">
              <label>Receiving Contact</label>
              <input type="text" defaultValue={leadData.contactName || 'Facilities Manager'} />
            </div>
          </div>
        </div>

        <div className="form-section">
          <h4>Installation Requirements</h4>
          <div className="checkbox-list">
            <label className="checkbox-item">
              <input type="checkbox" defaultChecked />
              <span>WiFi 6 coverage in operational areas</span>
            </label>
            <label className="checkbox-item">
              <input type="checkbox" defaultChecked />
              <span>Charging stations installed</span>
            </label>
            <label className="checkbox-item">
              <input type="checkbox" />
              <span>Emergency stop buttons mounted</span>
            </label>
            <label className="checkbox-item">
              <input type="checkbox" defaultChecked />
              <span>Facility map uploaded to system</span>
            </label>
          </div>
        </div>
      </div>

      <div className="deployment-summary">
        <div className="summary-card">
          <h4>Order Summary</h4>
          <div className="summary-row">
            <span>Fleet</span>
            <strong>{leadData.estimatedRobots} Unitree Robots</strong>
          </div>
          <div className="summary-row">
            <span>Go-Live Target</span>
            <strong>{new Date(Date.now() + 35 * 24 * 60 * 60 * 1000).toLocaleDateString()}</strong>
          </div>
          <div className="summary-row">
            <span>Account Manager</span>
            <strong>Alex Chen • alex@robotfleet.com</strong>
          </div>
        </div>
      </div>

      <div className="funnel-actions">
        <button className="btn-secondary" onClick={() => setStage('contract')}>
          Back
        </button>
        <button className="btn-funnel-next" onClick={() => handleNext('complete')}>
          Confirm Deployment <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  const renderComplete = () => (
    <div className="funnel-stage complete">
      <div className="success-animation">
        <div className="success-circle">
          <CheckCircle size={64} />
        </div>
        <h2>Welcome to RFaaS!</h2>
        <p className="success-message">
          Your robot fleet deployment is confirmed. We'll be in touch within 24 hours 
          to begin your facility assessment.
        </p>
      </div>

      <div className="success-details">
        <div className="detail-card">
          <h4>What Happens Next</h4>
          <ol className="next-steps">
            <li>✉️ Welcome email with deployment timeline</li>
            <li>📞 Call from your Account Manager (Alex Chen)</li>
            <li>🏭 Site survey scheduled for next week</li>
            <li>🤖 Robots provisioned and tested</li>
            <li>🚚 Delivery to your facility</li>
          </ol>
        </div>

        <div className="detail-card">
          <h4>Your Dashboard Access</h4>
          <div className="access-info">
            <div className="access-row">
              <span>Portal URL</span>
              <code>https://dashboard.robotfleet.com</code>
            </div>
            <div className="access-row">
              <span>Email</span>
              <code>{leadData.email}</code>
            </div>
            <div className="access-row">
              <span>Temp Password</span>
              <code>RFaaS2024!</code>
            </div>
          </div>
        </div>
      </div>

      <div className="success-actions">
        <button className="btn-funnel-next" onClick={() => onComplete?.(leadData as LeadData)}>
          Go to Dashboard <ArrowRight size={18} />
        </button>
      </div>
    </div>
  );

  return (
    <div className="sales-funnel">
      {stage === 'landing' && renderLanding()}
      {stage === 'demo_booking' && renderDemoBooking()}
      {stage === 'simulation' && renderSimulation()}
      {stage === 'proposal' && renderProposal()}
      {stage === 'contract' && renderContract()}
      {stage === 'deployment' && renderDeployment()}
      {stage === 'complete' && renderComplete()}
    </div>
  );
}
