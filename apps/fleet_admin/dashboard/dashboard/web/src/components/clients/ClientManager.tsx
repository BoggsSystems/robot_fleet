import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Building2, Users, CreditCard, X, ChevronRight, CheckCircle, AlertCircle } from 'lucide-react';
import './ClientManager.css';

export type Client = {
  id: string;
  name: string;
  company: string;
  email: string;
  phone: string;
  status: 'active' | 'suspended' | 'trial' | 'onboarding';
  plan: 'starter' | 'professional' | 'enterprise';
  robotQuota: number;
  robotCount: number;
  fleetCount: number;
  createdAt: string;
  lastActive: string;
  notes: string;
  billingStatus: 'paid' | 'pending' | 'overdue';
};

interface ClientManagerProps {
  onSelectClient?: (client: Client) => void;
  onCancel?: () => void;
  selectable?: boolean;
}

const DEFAULT_CLIENTS: Client[] = [
  {
    id: 'client_1',
    name: 'John Smith',
    company: 'Acme Distribution',
    email: 'john@acme.com',
    phone: '+1 (555) 123-4567',
    status: 'active',
    plan: 'professional',
    robotQuota: 10,
    robotCount: 3,
    fleetCount: 1,
    createdAt: '2024-01-15',
    lastActive: '2024-03-17',
    notes: 'Primary warehouse automation client',
    billingStatus: 'paid',
  },
  {
    id: 'client_2',
    name: 'Sarah Chen',
    company: 'TechStart Inc',
    email: 'sarah@techstart.io',
    phone: '+1 (555) 987-6543',
    status: 'trial',
    plan: 'starter',
    robotQuota: 3,
    robotCount: 0,
    fleetCount: 0,
    createdAt: '2024-03-10',
    lastActive: '2024-03-17',
    notes: 'Office automation trial - evaluating G1',
    billingStatus: 'paid',
  },
];

const PLAN_OPTIONS = [
  { id: 'starter', name: 'Starter', quota: 3, price: '$1,500/robot/mo' },
  { id: 'professional', name: 'Professional', quota: 10, price: '$1,200/robot/mo' },
  { id: 'enterprise', name: 'Enterprise', quota: 50, price: 'Custom pricing' },
];

export function ClientManager({ onSelectClient, onCancel, selectable = false }: ClientManagerProps) {
  const [clients, setClients] = useState<Client[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingClient, setEditingClient] = useState<Client | null>(null);
  const [formData, setFormData] = useState({
    name: '',
    company: '',
    email: '',
    phone: '',
    plan: 'starter',
    notes: '',
  });
  const [filter, setFilter] = useState<'all' | 'active' | 'trial' | 'suspended'>('all');

  useEffect(() => {
    const stored = localStorage.getItem('clients');
    if (stored) {
      setClients(JSON.parse(stored));
    } else {
      setClients(DEFAULT_CLIENTS);
      localStorage.setItem('clients', JSON.stringify(DEFAULT_CLIENTS));
    }
  }, []);

  const saveClients = (newClients: Client[]) => {
    setClients(newClients);
    localStorage.setItem('clients', JSON.stringify(newClients));
  };

  const handleCreate = () => {
    if (!formData.name.trim() || !formData.email.trim()) return;

    const plan = PLAN_OPTIONS.find(p => p.id === formData.plan);
    const newClient: Client = {
      id: `client_${Date.now()}`,
      name: formData.name,
      company: formData.company,
      email: formData.email,
      phone: formData.phone,
      status: 'onboarding',
      plan: formData.plan as Client['plan'],
      robotQuota: plan?.quota || 3,
      robotCount: 0,
      fleetCount: 0,
      createdAt: new Date().toISOString().split('T')[0],
      lastActive: new Date().toISOString().split('T')[0],
      notes: formData.notes,
      billingStatus: 'pending',
    };

    saveClients([...clients, newClient]);
    setFormData({ name: '', company: '', email: '', phone: '', plan: 'starter', notes: '' });
    setShowCreateForm(false);
  };

  const handleUpdate = () => {
    if (!editingClient || !formData.name.trim()) return;

    const updated = clients.map(c =>
      c.id === editingClient.id
        ? { ...c, name: formData.name, company: formData.company, email: formData.email, phone: formData.phone, plan: formData.plan as Client['plan'], notes: formData.notes }
        : c
    );

    saveClients(updated);
    setEditingClient(null);
    setFormData({ name: '', company: '', email: '', phone: '', plan: 'starter', notes: '' });
  };

  const handleDelete = (clientId: string) => {
    if (!confirm('Are you sure you want to delete this client? All their robots and fleets will be unassigned.')) return;
    saveClients(clients.filter(c => c.id !== clientId));
  };

  const startEdit = (client: Client) => {
    setEditingClient(client);
    setFormData({
      name: client.name,
      company: client.company,
      email: client.email,
      phone: client.phone,
      plan: client.plan,
      notes: client.notes,
    });
  };

  const getStatusIcon = (status: Client['status']) => {
    switch (status) {
      case 'active': return <CheckCircle size={14} className="status-icon active" />;
      case 'trial': return <AlertCircle size={14} className="status-icon trial" />;
      case 'suspended': return <AlertCircle size={14} className="status-icon suspended" />;
      default: return null;
    }
  };

  const getStatusLabel = (status: Client['status']) => {
    switch (status) {
      case 'active': return 'Active';
      case 'trial': return 'Trial';
      case 'suspended': return 'Suspended';
      case 'onboarding': return 'Onboarding';
      default: return status;
    }
  };

  const filteredClients = filter === 'all' ? clients : clients.filter(c => c.status === filter);

  return (
    <div className="client-manager">
      <div className="client-header">
        <h2>Client Management</h2>
        <p>Manage your RFaaS customers</p>
      </div>

      {/* Filter Tabs */}
      <div className="client-filters">
        {(['all', 'active', 'trial', 'suspended'] as const).map(f => (
          <button
            key={f}
            className={`filter-tab ${filter === f ? 'active' : ''}`}
            onClick={() => setFilter(f)}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
            <span className="count">
              {f === 'all' ? clients.length : clients.filter(c => c.status === f).length}
            </span>
          </button>
        ))}
      </div>

      {/* Client List */}
      <div className="client-list">
        {filteredClients.map(client => (
          <div
            key={client.id}
            className={`client-card ${selectable ? 'selectable' : ''}`}
            onClick={() => selectable && onSelectClient?.(client)}
          >
            <div className="client-main">
              <div className="client-icon">
                <Building2 size={24} />
              </div>
              <div className="client-info">
                <div className="client-header-row">
                  <h4>{client.company}</h4>
                  <span className={`status-badge ${client.status}`}>
                    {getStatusIcon(client.status)}
                    {getStatusLabel(client.status)}
                  </span>
                </div>
                <p className="client-contact">{client.name} • {client.email}</p>
                <p className="client-notes">{client.notes || 'No notes'}</p>
                
                <div className="client-meta">
                  <span className="meta-item">
                    <Users size={12} />
                    {client.robotCount} / {client.robotQuota} robots
                  </span>
                  <span className="meta-item">
                    <CreditCard size={12} />
                    {client.plan}
                  </span>
                  <span className={`meta-item billing ${client.billingStatus}`}>
                    {client.billingStatus}
                  </span>
                </div>
              </div>
            </div>

            {!selectable && (
              <div className="client-actions">
                <button
                  className="btn-icon"
                  onClick={(e) => { e.stopPropagation(); startEdit(client); }}
                >
                  <Edit2 size={16} />
                </button>
                <button
                  className="btn-icon delete"
                  onClick={(e) => { e.stopPropagation(); handleDelete(client.id); }}
                >
                  <Trash2 size={16} />
                </button>
              </div>
            )}

            {selectable && (
              <ChevronRight size={20} className="select-arrow" />
            )}
          </div>
        ))}
      </div>

      {/* Create New Client Button */}
      {!showCreateForm && !editingClient && !selectable && (
        <button className="btn-create-client" onClick={() => setShowCreateForm(true)}>
          <Plus size={20} />
          Add New Client
        </button>
      )}

      {/* Create/Edit Form */}
      {(showCreateForm || editingClient) && (
        <div className="client-form-overlay">
          <div className="client-form">
            <div className="form-header">
              <h3>{editingClient ? 'Edit Client' : 'Add New Client'}</h3>
              <button
                className="btn-close"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingClient(null);
                  setFormData({ name: '', company: '', email: '', phone: '', plan: 'starter', notes: '' });
                }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="form-fields">
              <div className="form-field">
                <label>Contact Name *</label>
                <input
                  type="text"
                  placeholder="Primary contact person"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Company Name</label>
                <input
                  type="text"
                  placeholder="Company or organization"
                  value={formData.company}
                  onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                />
              </div>

              <div className="form-row">
                <div className="form-field">
                  <label>Email *</label>
                  <input
                    type="email"
                    placeholder="contact@company.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  />
                </div>

                <div className="form-field">
                  <label>Phone</label>
                  <input
                    type="tel"
                    placeholder="+1 (555) 123-4567"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  />
                </div>
              </div>

              <div className="form-field">
                <label>Subscription Plan</label>
                <div className="plan-options">
                  {PLAN_OPTIONS.map(plan => (
                    <div
                      key={plan.id}
                      className={`plan-card ${formData.plan === plan.id ? 'selected' : ''}`}
                      onClick={() => setFormData({ ...formData, plan: plan.id })}
                    >
                      <div className="plan-name">{plan.name}</div>
                      <div className="plan-quota">{plan.quota} robots</div>
                      <div className="plan-price">{plan.price}</div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-field">
                <label>Notes</label>
                <textarea
                  placeholder="Internal notes about this client..."
                  value={formData.notes}
                  onChange={(e) => setFormData({ ...formData, notes: e.target.value })}
                  rows={3}
                />
              </div>
            </div>

            <div className="form-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingClient(null);
                  setFormData({ name: '', company: '', email: '', phone: '', plan: 'starter', notes: '' });
                }}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={editingClient ? handleUpdate : handleCreate}
                disabled={!formData.name.trim() || !formData.email.trim()}
              >
                {editingClient ? 'Update Client' : 'Create Client'}
              </button>
            </div>
          </div>
        </div>
      )}

      {onCancel && (
        <div className="client-actions-footer">
          <button className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
