import { useState, useEffect } from 'react';
import { Search, Plus, Eye, Edit2, Trash2, Calendar, TrendingUp, Users, DollarSign } from 'lucide-react';
import type { LeadData, FunnelStage } from '../sales/SalesFunnel';
import './LeadManager.css';

// Sample leads data
const SAMPLE_LEADS: LeadData[] = [
  {
    id: 'lead-001',
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
    createdAt: '2024-03-15',
    currentStage: 'proposal',
    notes: ['Referred by existing client', 'Interested in R1 and Go2 mix'],
  },
  {
    id: 'lead-002',
    companyName: 'Global Logistics Inc',
    contactName: 'Michael Chen',
    email: 'm.chen@globallogistics.com',
    phone: '+1 (555) 456-7890',
    industry: 'warehousing',
    facilitySize: '100000+',
    useCase: 'security_patrol',
    estimatedRobots: 8,
    timeline: '1-3_months',
    budget: '250k-500k',
    createdAt: '2024-03-14',
    currentStage: 'demo_booking',
    notes: ['Urgent requirement', 'Competitor quote received'],
  },
  {
    id: 'lead-003',
    companyName: 'HealthFirst Medical',
    contactName: 'Dr. Emily Rodriguez',
    email: 'e.rodriguez@healthfirst.com',
    phone: '+1 (555) 234-5678',
    industry: 'healthcare',
    facilitySize: '25000-50000',
    useCase: 'quality_inspection',
    estimatedRobots: 3,
    timeline: 'immediate',
    budget: '100k-250k',
    createdAt: '2024-03-13',
    currentStage: 'complete',
    notes: ['Pilot program requested', 'Budget approved'],
  },
  {
    id: 'lead-004',
    companyName: 'RetailMax Solutions',
    contactName: 'James Wilson',
    email: 'j.wilson@retailmax.com',
    phone: '+1 (555) 890-1234',
    industry: 'retail',
    facilitySize: '10000-25000',
    useCase: 'customer_service',
    estimatedRobots: 2,
    timeline: '6-12_months',
    budget: '50k-100k',
    createdAt: '2024-03-12',
    currentStage: 'contract',
    notes: ['Seasonal business', 'Starting with small pilot'],
  },
  {
    id: 'lead-005',
    companyName: 'InnovateTech Labs',
    contactName: 'Alex Kumar',
    email: 'a.kumar@innovatetech.com',
    phone: '+1 (555) 345-6789',
    industry: 'office',
    facilitySize: '10000-25000',
    useCase: 'research_assistant',
    estimatedRobots: 1,
    timeline: 'exploring',
    budget: '50k-100k',
    createdAt: '2024-03-11',
    currentStage: 'landing',
    notes: ['Research phase', 'Budget evaluation ongoing'],
  },
];

const FUNNEL_STAGES: FunnelStage[] = ['landing', 'demo_booking', 'simulation', 'proposal', 'contract', 'deployment', 'complete'];

const STAGE_CONFIG = {
  landing: { label: 'New Lead', color: '#94a3b8', icon: '🎯' },
  demo_booking: { label: 'Demo Scheduled', color: '#3b82f6', icon: '📅' },
  simulation: { label: 'Simulation Complete', color: '#8b5cf6', icon: '🎮' },
  proposal: { label: 'Proposal Sent', color: '#f59e0b', icon: '📄' },
  contract: { label: 'Contract Review', color: '#ef4444', icon: '📝' },
  deployment: { label: 'Deployment', color: '#10b981', icon: '🚀' },
  complete: { label: 'Client Onboarded', color: '#22c55e', icon: '✅' },
};

interface LeadManagerProps {
  onLeadSelect?: (lead: LeadData) => void;
  onConvertToClient?: (lead: LeadData) => void;
}

export function LeadManager({ onLeadSelect, onConvertToClient }: LeadManagerProps) {
  const [leads, setLeads] = useState<LeadData[]>(SAMPLE_LEADS);
  const [filteredLeads, setFilteredLeads] = useState<LeadData[]>(SAMPLE_LEADS);
  const [searchTerm, setSearchTerm] = useState('');
  const [stageFilter, setStageFilter] = useState<FunnelStage | 'all'>('all');
  const [industryFilter, setIndustryFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'createdAt' | 'companyName' | 'estimatedRobots'>('createdAt');

  // Filter leads based on search and filters
  useEffect(() => {
    let filtered = leads;

    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(lead => 
        lead.companyName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.contactName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        lead.email.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Stage filter
    if (stageFilter !== 'all') {
      filtered = filtered.filter(lead => lead.currentStage === stageFilter);
    }

    // Industry filter
    if (industryFilter !== 'all') {
      filtered = filtered.filter(lead => lead.industry === industryFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'createdAt':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        case 'companyName':
          return a.companyName.localeCompare(b.companyName);
        case 'estimatedRobots':
          return b.estimatedRobots - a.estimatedRobots;
        default:
          return 0;
      }
    });

    setFilteredLeads(filtered);
  }, [leads, searchTerm, stageFilter, industryFilter, sortBy]);

  const getStageBadge = (stage: FunnelStage) => {
    const config = STAGE_CONFIG[stage];
    return (
      <span 
        className="stage-badge" 
        style={{ 
          backgroundColor: `${config.color}20`, 
          color: config.color,
          border: `1px solid ${config.color}40`
        }}
      >
        <span className="stage-icon">{config.icon}</span>
        {config.label}
      </span>
    );
  };

  const getIndustryName = (industryId: string) => {
    const industries: Record<string, string> = {
      manufacturing: 'Manufacturing',
      warehousing: 'Warehousing & Logistics',
      retail: 'Retail & E-commerce',
      healthcare: 'Healthcare',
      hospitality: 'Hospitality',
      office: 'Corporate Office',
    };
    return industries[industryId] || industryId;
  };

  const getUseCaseName = (useCaseId: string) => {
    const useCases: Record<string, string> = {
      automated_material_handling: 'Automated Material Handling',
      security_patrol: 'Security & Patrol',
      quality_inspection: 'Quality Inspection',
      customer_service: 'Customer Service',
      cleaning_maintenance: 'Cleaning & Maintenance',
      research_assistant: 'Research & Lab Assistant',
    };
    return useCases[useCaseId] || useCaseId;
  };

  const getBudgetRange = (budget: string) => {
    const budgets: Record<string, string> = {
      '50k-100k': '$50K - $100K',
      '100k-250k': '$100K - $250K',
      '250k-500k': '$250K - $500K',
      '500k+': '$500K+',
    };
    return budgets[budget] || budget;
  };

  const handleDeleteLead = (leadId: string) => {
    setLeads(prev => prev.filter(lead => lead.id !== leadId));
  };

  const handleConvertToClient = (lead: LeadData) => {
    // Update lead stage to complete
    setLeads(prev => prev.map(l => 
      l.id === lead.id ? { ...l, currentStage: 'complete' as FunnelStage } : l
    ));
    onConvertToClient?.(lead);
  };

  const totalValue = filteredLeads.reduce((sum, lead) => {
    const budgetMap: Record<string, number> = {
      '50k-100k': 75000,
      '100k-250k': 175000,
      '250k-500k': 375000,
      '500k+': 750000,
    };
    return sum + (budgetMap[lead.budget] || 0);
  }, 0);

  const stageCounts = FUNNEL_STAGES.reduce((acc, stage) => {
    acc[stage] = leads.filter(lead => lead.currentStage === stage).length;
    return acc;
  }, {} as Record<FunnelStage, number>);

  return (
    <div className="lead-manager">
      <div className="lead-header">
        <h1>Sales Funnel Management</h1>
        <div className="header-stats">
          <div className="stat-card">
            <div className="stat-icon">
              <Users size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-number">{filteredLeads.length}</span>
              <span className="stat-label">Total Leads</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <TrendingUp size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-number">{stageCounts.complete || 0}</span>
              <span className="stat-label">Converted</span>
            </div>
          </div>
          <div className="stat-card">
            <div className="stat-icon">
              <DollarSign size={20} />
            </div>
            <div className="stat-content">
              <span className="stat-number">${(totalValue / 1000000).toFixed(1)}M</span>
              <span className="stat-label">Pipeline Value</span>
            </div>
          </div>
        </div>
      </div>

      <div className="lead-controls">
        <div className="search-bar">
          <Search size={18} className="search-icon" />
          <input
            type="text"
            placeholder="Search leads..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="filter-controls">
          <select
            value={stageFilter}
            onChange={(e) => setStageFilter(e.target.value as FunnelStage | 'all')}
            className="filter-select"
          >
            <option value="all">All Stages</option>
            {Object.entries(STAGE_CONFIG).map(([key, config]) => (
              <option key={key} value={key}>
                {config.icon} {config.label}
              </option>
            ))}
          </select>

          <select
            value={industryFilter}
            onChange={(e) => setIndustryFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Industries</option>
            <option value="manufacturing">Manufacturing</option>
            <option value="warehousing">Warehousing & Logistics</option>
            <option value="retail">Retail & E-commerce</option>
            <option value="healthcare">Healthcare</option>
            <option value="hospitality">Hospitality</option>
            <option value="office">Corporate Office</option>
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'createdAt' | 'companyName' | 'estimatedRobots')}
            className="filter-select"
          >
            <option value="createdAt">Sort by Date</option>
            <option value="companyName">Sort by Company</option>
            <option value="estimatedRobots">Sort by Fleet Size</option>
          </select>
        </div>

        <button 
          className="btn-add-lead"
          onClick={() => {
            const newLead: LeadData = {
              id: `lead-${Date.now()}`,
              companyName: '',
              contactName: '',
              email: '',
              phone: '',
              industry: 'manufacturing',
              facilitySize: '25000-50000',
              useCase: 'automated_material_handling',
              estimatedRobots: 3,
              timeline: '3-6_months',
              budget: '100k-250k',
              createdAt: new Date().toISOString().split('T')[0],
              currentStage: 'landing',
              notes: [],
            };
            setLeads(prev => [newLead, ...prev]);
          }}
        >
          <Plus size={16} />
          Add Lead
        </button>
      </div>

      <div className="lead-table-container">
        <table className="lead-table">
          <thead>
            <tr>
              <th>Company</th>
              <th>Contact</th>
              <th>Industry</th>
              <th>Use Case</th>
              <th>Fleet Size</th>
              <th>Budget</th>
              <th>Stage</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredLeads.map(lead => (
              <tr key={lead.id} className="lead-row">
                <td className="company-cell">
                  <div className="company-info">
                    <strong>{lead.companyName}</strong>
                    <span className="contact-email">{lead.email}</span>
                  </div>
                </td>
                <td className="contact-cell">
                  <div className="contact-info">
                    <span>{lead.contactName}</span>
                    <span className="contact-phone">{lead.phone}</span>
                  </div>
                </td>
                <td className="industry-cell">
                  <span className="industry-badge">
                    {getIndustryName(lead.industry)}
                  </span>
                </td>
                <td className="usecase-cell">
                  <span className="usecase-text">
                    {getUseCaseName(lead.useCase)}
                  </span>
                </td>
                <td className="fleet-cell">
                  <div className="fleet-info">
                    <span className="robot-count">{lead.estimatedRobots}</span>
                    <span className="robot-label">robots</span>
                  </div>
                </td>
                <td className="budget-cell">
                  <span className="budget-text">{getBudgetRange(lead.budget)}</span>
                </td>
                <td className="stage-cell">
                  {getStageBadge(lead.currentStage)}
                </td>
                <td className="date-cell">
                  <div className="date-info">
                    <Calendar size={14} />
                    <span>{new Date(lead.createdAt).toLocaleDateString()}</span>
                  </div>
                </td>
                <td className="actions-cell">
                  <div className="action-buttons">
                    <button 
                      className="btn-action btn-view"
                      onClick={() => onLeadSelect?.(lead)}
                      title="View Lead Details"
                    >
                      <Eye size={14} />
                    </button>
                    <button 
                      className="btn-action btn-edit"
                      onClick={() => onLeadSelect?.(lead)}
                      title="Edit Lead"
                    >
                      <Edit2 size={14} />
                    </button>
                    {lead.currentStage !== 'complete' && (
                      <button 
                        className="btn-action btn-convert"
                        onClick={() => handleConvertToClient(lead)}
                        title="Convert to Client"
                      >
                        <Users size={14} />
                      </button>
                    )}
                    <button 
                      className="btn-action btn-delete"
                      onClick={() => handleDeleteLead(lead.id)}
                      title="Delete Lead"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredLeads.length === 0 && (
        <div className="empty-leads">
          <div className="empty-icon">🎯</div>
          <h3>No leads found</h3>
          <p>Try adjusting your search or filters, or add a new lead to get started.</p>
        </div>
      )}
    </div>
  );
}
