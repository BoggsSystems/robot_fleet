import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { clientAPI } from '../services/api';
import { Client } from '../types';
import CreateClientWizard from '../components/CreateClientWizard';

// Simple notification function
const showNotification = (message: string, type: 'success' | 'error' | 'info') => {
  // Create notification container
  const notification = document.createElement('div');
  const bgColor = type === 'success' ? 'linear-gradient(135deg, #10b981 0%, #059669 100%)' : 
                   type === 'error' ? 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)' : 
                   'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)';
  const icon = type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️';
  const title = type === 'success' ? 'Success!' : type === 'error' ? 'Error!' : 'Info!';
  
  // Set styles directly instead of using innerHTML
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: ${bgColor};
    color: white;
    padding: 16px 20px;
    border-radius: 12px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
    z-index: 10000;
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 300px;
    max-width: 400px;
    transform: translateX(500px);
    opacity: 0;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  `;
  
  // Create icon element
  const iconElement = document.createElement('span');
  iconElement.style.cssText = 'font-size: 20px;';
  iconElement.textContent = icon;
  
  // Create content container
  const contentDiv = document.createElement('div');
  
  // Create title element
  const titleElement = document.createElement('div');
  titleElement.style.cssText = 'font-size: 14px; font-weight: 600; margin-bottom: 4px;';
  titleElement.textContent = title;
  
  // Create message element
  const messageElement = document.createElement('div');
  messageElement.style.cssText = 'font-size: 13px; opacity: 0.9;';
  messageElement.textContent = message;
  
  // Create close button
  const closeButton = document.createElement('button');
  closeButton.style.cssText = `
    background: rgba(255, 255, 255, 0.2);
    border: none;
    border-radius: 6px;
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: white;
    font-size: 16px;
    transition: background 0.2s;
  `;
  closeButton.textContent = '×';
  closeButton.onclick = () => notification.remove();
  
  // Assemble the notification
  contentDiv.appendChild(titleElement);
  contentDiv.appendChild(messageElement);
  notification.appendChild(iconElement);
  notification.appendChild(contentDiv);
  notification.appendChild(closeButton);
  
  // Add to DOM
  document.body.appendChild(notification);
  
  // Animate in
  setTimeout(() => {
    notification.style.transform = 'translateX(0)';
    notification.style.opacity = '1';
  }, 10);
  
  // Auto-remove after 3 seconds
  setTimeout(() => {
    if (notification.parentElement) {
      notification.style.transform = 'translateX(500px)';
      notification.style.opacity = '0';
      setTimeout(() => notification.remove(), 300);
    }
  }, 3000);
};

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

  const handleGenerateAndCopyMagicLink = async (clientId: string, clientEmail: string) => {
    try {
      const response = await clientAPI.generateMagicLink(clientId);
      
      // Copy to clipboard
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(response.magicLinkUrl);
      } else {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = response.magicLinkUrl;
        textArea.style.position = 'fixed';
        textArea.style.left = '-999999px';
        textArea.style.top = '-999999px';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      
      // Show elegant success message
      showNotification('Magic link copied to clipboard', 'success');
      
      const successMessage = document.createElement('div');
      successMessage.innerHTML = `
        <div style="
          position: fixed;
          top: 20px;
          right: 20px;
          background: linear-gradient(135deg, #10b981 0%, #059669 100%);
          color: white;
          padding: 16px 20px;
          border-radius: 12px;
          box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
          z-index: 1000;
          display: flex;
          align-items: center;
          gap: 12px;
          min-width: 300px;
          max-width: 400px;
          animation: slideIn 0.3s ease-out;
          backdrop-filter: blur(10px);
          border: 1px solid rgba(255, 255, 255, 0.2);
        ">
          <span style="font-size: 20px;">✅</span>
          <div>
            <div style="font-size: 14px; font-weight: 600; margin-bottom: 4px;">Success!</div>
            <div style="font-size: 13px; opacity: 0.9;">Magic link copied to clipboard</div>
          </div>
          <button onclick="this.parentElement.remove()" style="
            background: rgba(255, 255, 255, 0.2);
            border: none;
            border-radius: 6px;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            color: white;
            font-size: 16px;
            transition: background 0.2s;
          ">×</button>
        </div>
      `;
      document.body.appendChild(successMessage);
      
      // Auto-remove after 3 seconds
      setTimeout(() => {
        if (successMessage.parentElement) {
          successMessage.remove();
        }
      }, 3000);
      
    } catch (err: any) {
      showNotification(err.response?.data?.error || 'Failed to generate magic link', 'error');
    }
  };

  const handleSendMagicLink = async (clientId: string, clientEmail: string) => {
    try {
      const response = await clientAPI.sendMagicLink(clientId);
      showNotification(`Magic link sent to ${clientEmail}`, 'success');
    } catch (err: any) {
      showNotification(err.response?.data?.error || 'Failed to send magic link', 'error');
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
                    <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end', flexWrap: 'wrap' }}>
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
                        onClick={() => handleGenerateAndCopyMagicLink(client.id, client.email)}
                        disabled={client.status === 'suspended'}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: client.status === 'suspended' ? '#64748b20' : '#10b98120',
                          color: client.status === 'suspended' ? '#64748b' : '#10b981',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '13px',
                          fontWeight: 500,
                          cursor: client.status === 'suspended' ? 'not-allowed' : 'pointer'
                        }}
                      >
                        {client.status === 'suspended' ? 'Suspended' : 'Generate & Copy'}
                      </button>
                      <button
                        onClick={() => handleSendMagicLink(client.id, client.email)}
                        disabled={client.status === 'suspended'}
                        style={{
                          padding: '6px 12px',
                          backgroundColor: client.status === 'suspended' ? '#64748b20' : '#05966920',
                          color: client.status === 'suspended' ? '#64748b' : '#059669',
                          border: 'none',
                          borderRadius: '6px',
                          fontSize: '13px',
                          fontWeight: 500,
                          cursor: client.status === 'suspended' ? 'not-allowed' : 'pointer'
                        }}
                      >
                        {client.status === 'suspended' ? 'Suspended' : 'Send Email'}
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
