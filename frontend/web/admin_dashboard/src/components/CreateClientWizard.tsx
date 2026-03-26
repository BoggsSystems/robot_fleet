import React, { useState } from 'react';
import { clientAPI } from '../services/api';

interface CreateClientWizardProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

type IndustryType = 'manufacturing' | 'commercial_real_estate' | 'healthcare' | 'education' | 'logistics' | 'residential' | 'personal_use' | null;

interface WizardData {
  industry: IndustryType;
  entityType: 'business' | 'personal';
  name: string;
  email: string;
  phone: string;
  taxId: string;
  locations: Array<{
    name: string;
    address: string;
    type: 'primary' | 'secondary' | 'seasonal';
    classification: 'indoor' | 'outdoor' | 'mixed';
    size: string;
    operatingHours: string;
  }>;
  plan: 'hobby' | 'pro' | 'business' | 'enterprise';
  fleetSize: number;
  deploymentPriority: 'standard' | 'expedited';
  integrations: string[];
}

const INDUSTRIES = [
  { id: 'manufacturing', icon: '🏭', label: 'Manufacturing', description: 'Factory floors, assembly lines, production facilities' },
  { id: 'commercial_real_estate', icon: '🏢', label: 'Commercial Real Estate', description: 'Office buildings, retail centers, co-working spaces' },
  { id: 'healthcare', icon: '🏥', label: 'Healthcare', description: 'Hospitals, clinics, elder care facilities' },
  { id: 'education', icon: '🎓', label: 'Education', description: 'Campuses, research facilities, training centers' },
  { id: 'logistics', icon: '🚛', label: 'Logistics & Distribution', description: 'Warehouses, fulfillment centers, ports' },
  { id: 'residential', icon: '🏠', label: 'Residential / Property Management', description: 'Apartment complexes, HOA communities' },
  { id: 'personal_use', icon: '👤', label: 'Personal Use', description: 'Home automation, vacation properties, estate management' },
] as const;

const PLANS = [
  { id: 'hobby', name: 'Hobby', price: 99, maxRobots: 2, features: ['2 robots', 'Basic support', 'Mobile app access'] },
  { id: 'pro', name: 'Pro', price: 499, maxRobots: 10, features: ['10 robots', 'Priority support', 'API access', 'Analytics'] },
  { id: 'business', name: 'Business', price: 2000, maxRobots: 50, features: ['50 robots', '24/7 support', 'Dedicated manager', 'Custom integrations'] },
  { id: 'enterprise', name: 'Enterprise', price: 0, maxRobots: 500, features: ['Unlimited robots', 'White-label options', 'SLA guarantee', 'On-premise option'] },
] as const;

const INTEGRATION_OPTIONS = [
  'Security Systems',
  'HVAC / Climate Control',
  'Access Control',
  'Existing IoT Platform',
  'Building Management System',
  'ERP / WMS',
];

const CreateClientWizard: React.FC<CreateClientWizardProps> = ({ isOpen, onClose, onSuccess }) => {
  const [step, setStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [data, setData] = useState<WizardData>({
    industry: null,
    entityType: 'business',
    name: '',
    email: '',
    phone: '',
    taxId: '',
    locations: [{ name: '', address: '', type: 'primary', classification: 'indoor', size: '', operatingHours: '24/7' }],
    plan: 'pro',
    fleetSize: 1,
    deploymentPriority: 'standard',
    integrations: [],
  });

  const totalSteps = 5;

  const updateData = (updates: Partial<WizardData>) => {
    setData(prev => ({ ...prev, ...updates }));
  };

  const handleIndustrySelect = (industry: IndustryType) => {
    const isPersonal = industry === 'personal_use';
    updateData({ 
      industry, 
      entityType: isPersonal ? 'personal' : 'business',
      plan: isPersonal ? 'hobby' : 'pro'
    });
  };

  const fillTestData = () => {
    updateData({
      name: 'John Doe',
      email: 'john.doe@test.com',
      phone: '(555) 123-4567',
      locations: [{
        name: 'My Home',
        address: '123 Test Street, Test City, TC 12345',
        type: 'primary',
        classification: 'indoor',
        size: '3,000 sq ft',
        operatingHours: '24/7'
      }],
      fleetSize: 1,
      deploymentPriority: 'standard',
      integrations: ['Security Systems']
    });
  };

  const addLocation = () => {
    setData(prev => ({
      ...prev,
      locations: [...prev.locations, { name: '', address: '', type: 'secondary', classification: 'indoor', size: '', operatingHours: '24/7' }]
    }));
  };

  const removeLocation = (index: number) => {
    setData(prev => ({
      ...prev,
      locations: prev.locations.filter((_, i) => i !== index)
    }));
  };

  const updateLocation = (index: number, updates: Partial<WizardData['locations'][0]>) => {
    setData(prev => ({
      ...prev,
      locations: prev.locations.map((loc, i) => i === index ? { ...loc, ...updates } : loc)
    }));
  };

  const toggleIntegration = (integration: string) => {
    setData(prev => ({
      ...prev,
      integrations: prev.integrations.includes(integration)
        ? prev.integrations.filter(i => i !== integration)
        : [...prev.integrations, integration]
    }));
  };

  const formatPhoneNumber = (value: string): string => {
    // Strip all non-numeric characters
    const numbers = value.replace(/\D/g, '');
    
    // Handle international numbers (starts with 1 and more than 10 digits)
    if (numbers.length > 10 && numbers.startsWith('1')) {
      const country = numbers.slice(0, numbers.length - 10);
      const area = numbers.slice(-10, -7);
      const prefix = numbers.slice(-7, -4);
      const line = numbers.slice(-4);
      return `+${country} (${area}) ${prefix}-${line}`;
    }
    
    // Handle US/Canada 10-digit numbers
    if (numbers.length >= 10) {
      const area = numbers.slice(0, 3);
      const prefix = numbers.slice(3, 6);
      const line = numbers.slice(6, 10);
      return `(${area}) ${prefix}-${line}`;
    }
    
    // Partial formatting for incomplete numbers
    if (numbers.length >= 6) {
      return `(${numbers.slice(0, 3)}) ${numbers.slice(3, 6)}-${numbers.slice(6)}`;
    }
    if (numbers.length >= 3) {
      return `(${numbers.slice(0, 3)}) ${numbers.slice(3)}`;
    }
    
    return numbers;
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    
    const payload = {
      name: data.name,
      email: data.email,
      phone: data.phone,
      plan: data.plan,
      industry: data.industry,
      entityType: data.entityType,
      taxId: data.taxId,
      locations: data.locations,
      fleetSize: data.fleetSize,
      deploymentPriority: data.deploymentPriority,
      integrations: data.integrations,
    };
    
    console.log('Sending payload:', JSON.stringify(payload, null, 2));
    
    try {
      const response = await clientAPI.createClient(payload);
      console.log('Create client response:', response);
      onSuccess();
      onClose();
    } catch (err: any) {
      console.error('Create client error:', err);
      console.error('Error response data:', JSON.stringify(err.response?.data, null, 2));
      console.error('Error status:', err.response?.status);
      console.error('Error headers:', err.response?.headers);
      const errorMsg = err.response?.data?.detail || err.response?.data?.error || JSON.stringify(err.response?.data) || 'Failed to create client';
      alert(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const canProceed = () => {
    switch (step) {
      case 1:
        return data.industry !== null;
      case 2:
        return data.name && data.email;
      case 3:
        return data.locations.every(loc => loc.name && loc.address);
      case 4:
        return data.plan && data.fleetSize > 0;
      default:
        return true;
    }
  };

  const goToStep = (newStep: number) => {
    if (newStep >= 1 && newStep <= totalSteps) {
      setStep(newStep);
    }
  };

  const renderStep1 = () => (
    <div>
      <h2 style={{ fontSize: '24px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
        Select Industry
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
        What type of organization or use case is this for?
      </p>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        {INDUSTRIES.slice(0, 6).map((ind) => (
          <button
            key={ind.id}
            onClick={() => handleIndustrySelect(ind.id as IndustryType)}
            style={{
              padding: '24px',
              backgroundColor: data.industry === ind.id ? '#3b82f620' : '#1e293b',
              border: `2px solid ${data.industry === ind.id ? '#3b82f6' : '#334155'}`,
              borderRadius: '12px',
              cursor: 'pointer',
              textAlign: 'left',
              transition: 'all 0.2s',
            }}
          >
            <div style={{ fontSize: '32px', marginBottom: '12px' }}>{ind.icon}</div>
            <div style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
              {ind.label}
            </div>
            <div style={{ fontSize: '13px', color: '#94a3b8', lineHeight: '1.4' }}>
              {ind.description}
            </div>
          </button>
        ))}
      </div>
      
      <button
        onClick={() => handleIndustrySelect('personal_use')}
        style={{
          width: '100%',
          padding: '24px',
          backgroundColor: data.industry === 'personal_use' ? '#3b82f620' : '#1e293b',
          border: `2px solid ${data.industry === 'personal_use' ? '#3b82f6' : '#334155'}`,
          borderRadius: '12px',
          cursor: 'pointer',
          textAlign: 'center',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '16px',
        }}
      >
        <span style={{ fontSize: '32px' }}>👤</span>
        <div style={{ textAlign: 'left' }}>
          <div style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
            Personal Use
          </div>
          <div style={{ fontSize: '14px', color: '#94a3b8' }}>
            Home automation, vacation properties, estate management - for individuals and families
          </div>
        </div>
      </button>
    </div>
  );

  const renderStep2 = () => (
    <div>
      <h2 style={{ fontSize: '24px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
        {data.entityType === 'personal' ? 'Personal Information' : 'Organization Profile'}
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
        {data.entityType === 'personal' 
          ? 'Tell us about yourself and your properties'
          : 'Basic information about the organization'}
      </p>
      
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '8px' }}>
            {data.entityType === 'personal' ? 'Full Name' : 'Organization Name'} *
          </label>
          <input
            type="text"
            value={data.name}
            onChange={(e) => updateData({ name: e.target.value })}
            placeholder={data.entityType === 'personal' ? 'John Smith' : 'Acme Corporation'}
            style={{
              width: '100%',
              padding: '12px 16px',
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '14px',
            }}
          />
        </div>
        
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '8px' }}>
            Email Address *
          </label>
          <input
            type="email"
            value={data.email}
            onChange={(e) => updateData({ email: e.target.value })}
            placeholder="name@example.com"
            style={{
              width: '100%',
              padding: '12px 16px',
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '14px',
            }}
          />
        </div>
        
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '8px' }}>
            Phone Number
          </label>
          <input
            type="tel"
            value={data.phone}
            onChange={(e) => updateData({ phone: formatPhoneNumber(e.target.value) })}
            placeholder="(555) 123-4567"
            style={{
              width: '100%',
              padding: '12px 16px',
              backgroundColor: '#0f172a',
              border: '1px solid #334155',
              borderRadius: '8px',
              color: '#f8fafc',
              fontSize: '14px',
            }}
          />
        </div>
        
        {data.entityType === 'business' && (
          <div>
            <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '8px' }}>
              Tax ID / Business Number
            </label>
            <input
              type="text"
              value={data.taxId}
              onChange={(e) => updateData({ taxId: e.target.value })}
              placeholder="XX-XXXXXXX"
              style={{
                width: '100%',
                padding: '12px 16px',
                backgroundColor: '#0f172a',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: '#f8fafc',
                fontSize: '14px',
              }}
            />
          </div>
        )}
      </div>
    </div>
  );

  const renderStep3 = () => (
    <div>
      <h2 style={{ fontSize: '24px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
        Locations & Properties
      </h2>
      <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
        Define the physical sites where robots will be deployed
      </p>
      
      {data.locations.map((loc, index) => (
        <div 
          key={index}
          style={{ 
            backgroundColor: '#1e293b', 
            borderRadius: '12px', 
            padding: '20px', 
            marginBottom: '16px',
            border: '1px solid #334155'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
            <span style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>
              Location {index + 1}
            </span>
            {data.locations.length > 1 && (
              <button
                onClick={() => removeLocation(index)}
                style={{
                  padding: '6px 12px',
                  backgroundColor: '#dc262620',
                  border: 'none',
                  borderRadius: '6px',
                  color: '#dc2626',
                  fontSize: '13px',
                  cursor: 'pointer',
                }}
              >
                Remove
              </button>
            )}
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#94a3b8', marginBottom: '4px' }}>
                Location Name *
              </label>
              <input
                type="text"
                value={loc.name}
                onChange={(e) => updateLocation(index, { name: e.target.value })}
                placeholder={index === 0 ? "Main Office" : "Secondary Location"}
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '14px',
                }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#94a3b8', marginBottom: '4px' }}>
                Address *
              </label>
              <input
                type="text"
                value={loc.address}
                onChange={(e) => updateLocation(index, { address: e.target.value })}
                placeholder="123 Main St, City, State ZIP"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '14px',
                }}
              />
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#94a3b8', marginBottom: '4px' }}>
                  Type
                </label>
                <select
                  value={loc.type}
                  onChange={(e) => updateLocation(index, { type: e.target.value as any })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    color: '#f8fafc',
                    fontSize: '14px',
                  }}
                >
                  <option value="primary">Primary</option>
                  <option value="secondary">Secondary</option>
                  <option value="seasonal">Seasonal</option>
                </select>
              </div>
              
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#94a3b8', marginBottom: '4px' }}>
                  Classification
                </label>
                <select
                  value={loc.classification}
                  onChange={(e) => updateLocation(index, { classification: e.target.value as any })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    color: '#f8fafc',
                    fontSize: '14px',
                  }}
                >
                  <option value="indoor">Indoor</option>
                  <option value="outdoor">Outdoor</option>
                  <option value="mixed">Mixed</option>
                </select>
              </div>
              
              <div>
                <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#94a3b8', marginBottom: '4px' }}>
                  Operating Hours
                </label>
                <select
                  value={loc.operatingHours}
                  onChange={(e) => updateLocation(index, { operatingHours: e.target.value })}
                  style={{
                    width: '100%',
                    padding: '10px 14px',
                    backgroundColor: '#0f172a',
                    border: '1px solid #334155',
                    borderRadius: '6px',
                    color: '#f8fafc',
                    fontSize: '14px',
                  }}
                >
                  <option value="24/7">24/7</option>
                  <option value="business">Business Hours</option>
                  <option value="seasonal">Seasonal</option>
                </select>
              </div>
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '13px', fontWeight: 500, color: '#94a3b8', marginBottom: '4px' }}>
                Size / Area
              </label>
              <input
                type="text"
                value={loc.size}
                onChange={(e) => updateLocation(index, { size: e.target.value })}
                placeholder="e.g., 50,000 sq ft, 5 acres, 12 rooms"
                style={{
                  width: '100%',
                  padding: '10px 14px',
                  backgroundColor: '#0f172a',
                  border: '1px solid #334155',
                  borderRadius: '6px',
                  color: '#f8fafc',
                  fontSize: '14px',
                }}
              />
            </div>
          </div>
        </div>
      ))}
      
      <button
        onClick={addLocation}
        style={{
          width: '100%',
          padding: '12px',
          backgroundColor: '#1e293b',
          border: '2px dashed #334155',
          borderRadius: '8px',
          color: '#94a3b8',
          fontSize: '14px',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '8px',
        }}
      >
        <span>+</span> Add Another Location
      </button>
    </div>
  );

  const renderStep4 = () => {
    const selectedPlan = PLANS.find(p => p.id === data.plan);
    
    return (
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
          Service Plan & Fleet
        </h2>
        <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
          Choose your subscription tier and robot deployment
        </p>
        
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '12px' }}>
            Select Plan
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
            {PLANS.map((plan) => (
              <button
                key={plan.id}
                onClick={() => updateData({ plan: plan.id as any, fleetSize: Math.min(data.fleetSize, plan.maxRobots) })}
                disabled={data.entityType === 'personal' && plan.id !== 'hobby'}
                style={{
                  padding: '16px',
                  backgroundColor: data.plan === plan.id ? '#3b82f620' : '#1e293b',
                  border: `2px solid ${data.plan === plan.id ? '#3b82f6' : '#334155'}`,
                  borderRadius: '10px',
                  cursor: data.entityType === 'personal' && plan.id !== 'hobby' ? 'not-allowed' : 'pointer',
                  opacity: data.entityType === 'personal' && plan.id !== 'hobby' ? 0.5 : 1,
                  textAlign: 'left',
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>{plan.name}</span>
                  <span style={{ fontSize: '18px', fontWeight: 700, color: '#3b82f6' }}>
                    {plan.price === 0 ? 'Custom' : `$${plan.price}/mo`}
                  </span>
                </div>
                <div style={{ fontSize: '13px', color: '#94a3b8', marginBottom: '8px' }}>
                  Up to {plan.maxRobots} robots
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
                  {plan.features.slice(0, 2).map((feature, i) => (
                    <span 
                      key={i}
                      style={{
                        fontSize: '11px',
                        padding: '2px 6px',
                        backgroundColor: '#0f172a',
                        borderRadius: '4px',
                        color: '#64748b',
                      }}
                    >
                      {feature}
                    </span>
                  ))}
                </div>
              </button>
            ))}
          </div>
        </div>
        
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '12px' }}>
            Robot Fleet Size
          </label>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <input
              type="range"
              min="1"
              max={selectedPlan?.maxRobots || 50}
              value={data.fleetSize}
              onChange={(e) => updateData({ fleetSize: parseInt(e.target.value) })}
              style={{ flex: 1 }}
            />
            <span style={{ 
              minWidth: '60px', 
              textAlign: 'center', 
              padding: '8px 16px', 
              backgroundColor: '#3b82f6', 
              borderRadius: '8px',
              color: 'white',
              fontWeight: 600,
            }}>
              {data.fleetSize}
            </span>
          </div>
        </div>
        
        <div style={{ marginBottom: '24px' }}>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '12px' }}>
            Deployment Priority
          </label>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => updateData({ deploymentPriority: 'standard' })}
              style={{
                flex: 1,
                padding: '16px',
                backgroundColor: data.deploymentPriority === 'standard' ? '#3b82f620' : '#1e293b',
                border: `2px solid ${data.deploymentPriority === 'standard' ? '#3b82f6' : '#334155'}`,
                borderRadius: '10px',
                cursor: 'pointer',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
                Standard
              </div>
              <div style={{ fontSize: '13px', color: '#94a3b8' }}>
                14 days deployment
              </div>
              <div style={{ fontSize: '12px', color: '#64748b', marginTop: '4px' }}>
                Included
              </div>
            </button>
            <button
              onClick={() => updateData({ deploymentPriority: 'expedited' })}
              style={{
                flex: 1,
                padding: '16px',
                backgroundColor: data.deploymentPriority === 'expedited' ? '#3b82f620' : '#1e293b',
                border: `2px solid ${data.deploymentPriority === 'expedited' ? '#3b82f6' : '#334155'}`,
                borderRadius: '10px',
                cursor: 'pointer',
                textAlign: 'center',
              }}
            >
              <div style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
                Expedited
              </div>
              <div style={{ fontSize: '13px', color: '#94a3b8' }}>
                3 days deployment
              </div>
              <div style={{ fontSize: '12px', color: '#f59e0b', marginTop: '4px' }}>
                +$500 fee
              </div>
            </button>
          </div>
        </div>
        
        <div>
          <label style={{ display: 'block', fontSize: '14px', fontWeight: 500, color: '#e2e8f0', marginBottom: '12px' }}>
            Integration Needs (Optional)
          </label>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {INTEGRATION_OPTIONS.map((integration) => (
              <button
                key={integration}
                onClick={() => toggleIntegration(integration)}
                style={{
                  padding: '8px 16px',
                  backgroundColor: data.integrations.includes(integration) ? '#3b82f620' : '#1e293b',
                  border: `1px solid ${data.integrations.includes(integration) ? '#3b82f6' : '#334155'}`,
                  borderRadius: '20px',
                  color: data.integrations.includes(integration) ? '#3b82f6' : '#94a3b8',
                  fontSize: '13px',
                  cursor: 'pointer',
                  transition: 'all 0.2s',
                }}
              >
                {data.integrations.includes(integration) ? '✓ ' : ''}{integration}
              </button>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderStep5 = () => {
    const selectedIndustry = INDUSTRIES.find(i => i.id === data.industry);
    const selectedPlan = PLANS.find(p => p.id === data.plan);
    const totalCost = (selectedPlan?.price || 0) + (data.deploymentPriority === 'expedited' ? 500 : 0);
    
    return (
      <div>
        <h2 style={{ fontSize: '24px', fontWeight: 600, color: '#f8fafc', marginBottom: '8px' }}>
          Review & Launch
        </h2>
        <p style={{ color: '#94a3b8', marginBottom: '24px' }}>
          Confirm all details before creating the client account
        </p>
        
        <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', padding: '20px', marginBottom: '16px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
            <span style={{ fontSize: '32px' }}>{selectedIndustry?.icon}</span>
            <div>
              <div style={{ fontSize: '18px', fontWeight: 600, color: '#f8fafc' }}>{data.name}</div>
              <div style={{ fontSize: '14px', color: '#94a3b8' }}>{selectedIndustry?.label} • {data.email}</div>
            </div>
          </div>
          
          <div style={{ borderTop: '1px solid #334155', paddingTop: '16px' }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Plan</div>
                <div style={{ fontSize: '14px', color: '#e2e8f0' }}>{selectedPlan?.name}</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Robot Fleet</div>
                <div style={{ fontSize: '14px', color: '#e2e8f0' }}>{data.fleetSize} robots</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Locations</div>
                <div style={{ fontSize: '14px', color: '#e2e8f0' }}>{data.locations.length} sites</div>
              </div>
              <div>
                <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>Deployment</div>
                <div style={{ fontSize: '14px', color: '#e2e8f0' }}>
                  {data.deploymentPriority === 'expedited' ? '3 days (expedited)' : '14 days (standard)'}
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <div style={{ backgroundColor: '#0f172a', borderRadius: '12px', padding: '20px', marginBottom: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
            <span style={{ fontSize: '14px', color: '#94a3b8' }}>Monthly Subscription</span>
            <span style={{ fontSize: '16px', color: '#f8fafc' }}>${selectedPlan?.price || 0}/mo</span>
          </div>
          {data.deploymentPriority === 'expedited' && (
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
              <span style={{ fontSize: '14px', color: '#94a3b8' }}>Expedited Deployment Fee</span>
              <span style={{ fontSize: '16px', color: '#f8fafc' }}>$500</span>
            </div>
          )}
          <div style={{ borderTop: '1px solid #334155', marginTop: '12px', paddingTop: '12px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ fontSize: '16px', fontWeight: 600, color: '#f8fafc' }}>First Month Total</span>
            <span style={{ fontSize: '24px', fontWeight: 700, color: '#3b82f6' }}>${totalCost}</span>
          </div>
        </div>
        
        <div style={{ fontSize: '13px', color: '#64748b', marginBottom: '16px' }}>
          By creating this client, you agree to the Platform Service Agreement. An email will be sent to {data.email} with onboarding instructions.
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div 
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 1000,
        padding: '24px',
      }}
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div 
        style={{
          backgroundColor: '#0f172a',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '700px',
          maxHeight: '90vh',
          overflow: 'hidden',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        {/* Header */}
        <div style={{ 
          padding: '24px 32px', 
          borderBottom: '1px solid #334155',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div>
            <h1 style={{ fontSize: '20px', fontWeight: 600, color: '#f8fafc', marginBottom: '4px' }}>
              Create New Client
            </h1>
            <p style={{ fontSize: '14px', color: '#94a3b8' }}>
              Step {step} of {totalSteps}
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              padding: '8px',
              backgroundColor: 'transparent',
              border: 'none',
              borderRadius: '6px',
              color: '#94a3b8',
              cursor: 'pointer',
              fontSize: '20px',
            }}
          >
            ×
          </button>
        </div>

        {/* Progress Bar */}
        <div style={{ 
          display: 'flex', 
          padding: '0 32px',
          marginTop: '20px',
          marginBottom: '8px',
        }}>
          {Array.from({ length: totalSteps }).map((_, i) => (
            <div key={i} style={{ flex: 1, display: 'flex', alignItems: 'center' }}>
              <div 
                style={{
                  width: i + 1 < step ? 8 : 24,
                  height: 8,
                  borderRadius: 4,
                  backgroundColor: i + 1 <= step ? '#3b82f6' : '#334155',
                  transition: 'all 0.3s',
                }}
              />
              {i < totalSteps - 1 && (
                <div 
                  style={{
                    flex: 1,
                    height: 2,
                    backgroundColor: i + 1 < step ? '#3b82f6' : '#334155',
                    margin: '0 4px',
                  }}
                />
              )}
            </div>
          ))}
        </div>

        {/* Content */}
        <div style={{ 
          flex: 1, 
          overflow: 'auto', 
          padding: '24px 32px',
        }}>
          {step === 1 && renderStep1()}
          {step === 2 && renderStep2()}
          {step === 3 && renderStep3()}
          {step === 4 && renderStep4()}
          {step === 5 && renderStep5()}
        </div>

        {/* Footer */}
        <div style={{ 
          padding: '24px 32px', 
          borderTop: '1px solid #334155',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button
              onClick={() => goToStep(step - 1)}
              disabled={step === 1}
              style={{
                padding: '12px 24px',
                backgroundColor: 'transparent',
                border: '1px solid #334155',
                borderRadius: '8px',
                color: step === 1 ? '#64748b' : '#f8fafc',
                fontSize: '14px',
                fontWeight: 500,
                cursor: step === 1 ? 'not-allowed' : 'pointer',
              }}
            >
              Back
            </button>
            <button
              onClick={fillTestData}
              style={{
                padding: '12px 24px',
                backgroundColor: '#f59e0b20',
                border: '1px solid #f59e0b',
                borderRadius: '8px',
                color: '#f59e0b',
                fontSize: '13px',
                fontWeight: 500,
                cursor: 'pointer',
              }}
            >
              Quick Fill Test Data
            </button>
          </div>
          
          {step < totalSteps ? (
            <button
              onClick={() => goToStep(step + 1)}
              disabled={!canProceed()}
              style={{
                padding: '12px 32px',
                backgroundColor: canProceed() ? '#3b82f6' : '#334155',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontSize: '14px',
                fontWeight: 500,
                cursor: canProceed() ? 'pointer' : 'not-allowed',
              }}
            >
              Next
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting}
              style={{
                padding: '12px 32px',
                backgroundColor: isSubmitting ? '#334155' : '#22c55e',
                border: 'none',
                borderRadius: '8px',
                color: 'white',
                fontSize: '14px',
                fontWeight: 500,
                cursor: isSubmitting ? 'not-allowed' : 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}
            >
              {isSubmitting ? (
                <>
                  <span style={{ animation: 'spin 1s linear infinite' }}>⟳</span>
                  Creating...
                </>
              ) : (
                'Create Client'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CreateClientWizard;
