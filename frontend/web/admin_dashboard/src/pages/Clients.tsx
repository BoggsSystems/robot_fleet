import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Client } from '../types';
import { clientAPI } from '../services/api';
import CreateClientWizard from '../components/CreateClientWizard';

const Clients: React.FC = () => {
  const [clients, setClients] = useState<Client[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [planFilter, setPlanFilter] = useState<string>('');
  const [isWizardOpen, setIsWizardOpen] = useState(false);

  useEffect(() => {
    fetchClients();
  }, [statusFilter, planFilter]);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const filters: { status?: string; plan?: string } = {};
      if (statusFilter) filters.status = statusFilter;
      if (planFilter) filters.plan = planFilter;
      
      const response = await clientAPI.getClients(filters);
      setClients(response.clients);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.error || 'Failed to load clients');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteClient = async (id: string) => {
    if (!window.confirm('Are you sure you want to suspend this client?')) {
      return;
    }
    
    try {
      await clientAPI.deleteClient(id);
      fetchClients();
    } catch (err: any) {
      alert(err.response?.data?.error || 'Failed to suspend client');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return { bg: '#22c55e20', text: '#22c55e' };
      case 'trial': return { bg: '#3b82f620', text: '#3b82f6' };
      case 'suspended': return { bg: '#dc262620', text: '#dc2626' };
      default: return { bg: '#64748b20', text: '#64748b' };
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
        <div style={{ fontSize: '24px', marginBottom: '16px' }}>⏳</div>
        <p>Loading clients...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ 
          backgroundColor: '#dc262620', 
          border: '1px solid #dc2626',
          borderRadius: '8px',
          padding: '20px',
          maxWidth: '500px',
          margin: '0 auto'
        }}>
          <p style={{ color: '#dc2626', fontSize: '16px', marginBottom: '8px' }}>Error loading clients</p>
          <p style={{ color: '#94a3b8', fontSize: '14px' }}>{error}</p>
          <button 
            onClick={fetchClients}
            style={{
              marginTop: '16px',
              padding: '8px 16px',
              backgroundColor: '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer'
            }}
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
            Client Management
          </h1>
          <p style={{ color: '#94a3b8' }}>Manage all client accounts and their fleets</p>
        </div>
        <button 
          onClick={() => setIsWizardOpen(true)}
          style={{
            padding: '12px 24px',
            backgroundColor: '#3b82f6',
            color: 'white',
            borderRadius: '8px',
            border: 'none',
            fontWeight: 500,
            cursor: 'pointer',
          }}
        >
          + Add Client
        </button>
      </div>

      {/* Filters */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '24px' }}>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          style={{
            padding: '10px 16px',
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#f8fafc',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="trial">Trial</option>
          <option value="suspended">Suspended</option>
        </select>
        
        <select
          value={planFilter}
          onChange={(e) => setPlanFilter(e.target.value)}
          style={{
            padding: '10px 16px',
            backgroundColor: '#1e293b',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#f8fafc',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          <option value="">All Plans</option>
          <option value="starter">Starter</option>
          <option value="professional">Professional</option>
          <option value="enterprise">Enterprise</option>
        </select>
        
        <button
          onClick={() => { setStatusFilter(''); setPlanFilter(''); }}
          style={{
            padding: '10px 16px',
            backgroundColor: 'transparent',
            border: '1px solid #334155',
            borderRadius: '8px',
            color: '#94a3b8',
            fontSize: '14px',
            cursor: 'pointer'
          }}
        >
          Clear Filters
        </button>
      </div>

      {/* Clients Table */}
      <div style={{ backgroundColor: '#1e293b', borderRadius: '12px', border: '1px solid #334155', overflow: 'hidden' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ backgroundColor: '#0f172a' }}>
              <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Client</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Status</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Plan</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Fleet</th>
              <th style={{ padding: '16px', textAlign: 'left', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>MRR</th>
              <th style={{ padding: '16px', textAlign: 'right', color: '#94a3b8', fontSize: '14px', fontWeight: 500 }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {clients.map((client) => {
              const statusColor = getStatusColor(client.status);
              return (
                <tr key={client.id} style={{ borderTop: '1px solid #334155' }}>
                  <td style={{ padding: '16px' }}>
                    <p style={{ fontSize: '16px', fontWeight: 500, color: '#f8fafc', marginBottom: '4px' }}>
                      {client.name}
                    </p>
                    <p style={{ fontSize: '13px', color: '#94a3b8' }}>
                      {client.warehouse?.location || client.locations?.[0]?.address || 'No location set'}
                    </p>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{
                      padding: '4px 12px',
                      borderRadius: '20px',
                      fontSize: '12px',
                      fontWeight: 500,
                      backgroundColor: statusColor.bg,
                      color: statusColor.text,
                      textTransform: 'capitalize'
                    }}>
                      {client.status}
                    </span>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ fontSize: '14px', color: '#e2e8f0', textTransform: 'capitalize' }}>
                      {client.plan}
                    </span>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ fontSize: '14px', color: '#e2e8f0' }}>
                      {client.fleet?.activeRobots || 0}/{client.fleet?.totalRobots || client.fleetSize || 0} active
                    </span>
                  </td>
                  <td style={{ padding: '16px' }}>
                    <span style={{ fontSize: '14px', color: '#e2e8f0' }}>
                      ${(client.subscription?.mrr || 0).toLocaleString()}
                    </span>
                  </td>
                  <td style={{ padding: '16px', textAlign: 'right' }}>
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                      <Link
                        to={`/clients/${client.id}`}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: '#3b82f620',
                          color: '#3b82f6',
                          borderRadius: '6px',
                          textDecoration: 'none',
                          fontSize: '13px',
                          fontWeight: 500
                        }}
                      >
                        View
                      </Link>
                      <button
                        onClick={() => handleDeleteClient(client.id)}
                        disabled={client.status === 'suspended'}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: client.status === 'suspended' ? '#64748b20' : '#dc262620',
                          color: client.status === 'suspended' ? '#64748b' : '#dc2626',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '13px',
                          fontWeight: 500,
                          cursor: client.status === 'suspended' ? 'not-allowed' : 'pointer'
                        }}
                      >
                        {client.status === 'suspended' ? 'Suspended' : 'Suspend'}
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        
        {clients.length === 0 && (
          <div style={{ padding: '40px', textAlign: 'center', color: '#94a3b8' }}>
            <p>No clients found matching your filters.</p>
          </div>
        )}
      </div>

      <CreateClientWizard
        isOpen={isWizardOpen}
        onClose={() => setIsWizardOpen(false)}
        onSuccess={fetchClients}
      />
    </div>
  );
};

export default Clients;
