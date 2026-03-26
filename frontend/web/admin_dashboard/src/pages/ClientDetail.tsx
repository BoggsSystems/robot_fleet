import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { clientAPI } from '../services/api';

const ClientDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [client, setClient] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchClient = async () => {
      if (!id) return;
      try {
        setLoading(true);
        const response = await clientAPI.getClient(id);
        setClient(response.client);
      } catch (err: any) {
        setError(err.response?.data?.error || 'Failed to load client');
      } finally {
        setLoading(false);
      }
    };
    fetchClient();
  }, [id]);

  if (loading) {
    return (
      <div style={{ padding: '32px', color: '#94a3b8' }}>
        <p>Loading client...</p>
      </div>
    );
  }

  if (error || !client) {
    return (
      <div style={{ padding: '32px' }}>
        <p style={{ color: '#dc2626' }}>{error || 'Client not found'}</p>
        <Link to="/clients" style={{ color: '#3b82f6' }}>Back to Clients</Link>
      </div>
    );
  }

  return (
    <div style={{ padding: '32px' }}>
      {/* Header */}
      <div style={{ marginBottom: '32px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '16px' }}>
          <Link to="/clients" style={{ color: '#94a3b8', textDecoration: 'none' }}>← Back</Link>
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div>
            <h1 style={{ fontSize: '28px', fontWeight: 700, color: '#f8fafc', marginBottom: '8px' }}>
              {client.name}
            </h1>
            <p style={{ color: '#94a3b8' }}>{client.email} • {client.entityType || 'business'}</p>
          </div>
          <span style={{
            padding: '8px 16px',
            borderRadius: '20px',
            fontSize: '14px',
            fontWeight: 500,
            backgroundColor: client.status === 'active' ? '#10b98120' : client.status === 'trial' ? '#f59e0b20' : '#64748b20',
            color: client.status === 'active' ? '#10b981' : client.status === 'trial' ? '#f59e0b' : '#94a3b8',
            textTransform: 'capitalize'
          }}>
            {client.status}
          </span>
        </div>
      </div>

      {/* Info Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '24px' }}>
        {/* Plan & Subscription */}
        <div style={{ backgroundColor: '#1e293b', padding: '24px', borderRadius: '12px', border: '1px solid #334155' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#94a3b8', marginBottom: '16px' }}>Plan & Subscription</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Plan</span>
              <span style={{ color: '#f8fafc', textTransform: 'capitalize' }}>{client.plan}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Monthly Revenue</span>
              <span style={{ color: '#f8fafc' }}>${(client.subscription?.mrr || 0).toLocaleString()}/mo</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Fleet Size</span>
              <span style={{ color: '#f8fafc' }}>{client.fleetSize || 0} robots</span>
            </div>
          </div>
        </div>

        {/* Contact */}
        <div style={{ backgroundColor: '#1e293b', padding: '24px', borderRadius: '12px', border: '1px solid #334155' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#94a3b8', marginBottom: '16px' }}>Contact Information</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <span style={{ color: '#94a3b8', fontSize: '13px' }}>Email</span>
              <p style={{ color: '#f8fafc' }}>{client.email}</p>
            </div>
            <div>
              <span style={{ color: '#94a3b8', fontSize: '13px' }}>Phone</span>
              <p style={{ color: '#f8fafc' }}>{client.phone || 'Not provided'}</p>
            </div>
            <div>
              <span style={{ color: '#94a3b8', fontSize: '13px' }}>Tax ID</span>
              <p style={{ color: '#f8fafc' }}>{client.taxId || 'Not provided'}</p>
            </div>
          </div>
        </div>

        {/* Locations */}
        <div style={{ backgroundColor: '#1e293b', padding: '24px', borderRadius: '12px', border: '1px solid #334155' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#94a3b8', marginBottom: '16px' }}>Locations ({client.locations?.length || 0})</h3>
          {client.locations?.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {client.locations.map((loc: any, i: number) => (
                <div key={i} style={{ padding: '12px', backgroundColor: '#0f172a', borderRadius: '8px' }}>
                  <p style={{ color: '#f8fafc', fontWeight: 500 }}>{loc.name}</p>
                  <p style={{ color: '#94a3b8', fontSize: '13px' }}>{loc.address}</p>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: '#64748b' }}>No locations configured</p>
          )}
        </div>

        {/* Fleet Status */}
        <div style={{ backgroundColor: '#1e293b', padding: '24px', borderRadius: '12px', border: '1px solid #334155' }}>
          <h3 style={{ fontSize: '16px', fontWeight: 600, color: '#94a3b8', marginBottom: '16px' }}>Fleet Status</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Total Robots</span>
              <span style={{ color: '#f8fafc' }}>{client.fleet?.totalRobots || client.fleetSize || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Active</span>
              <span style={{ color: '#10b981' }}>{client.fleet?.activeRobots || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Idle</span>
              <span style={{ color: '#f59e0b' }}>{client.fleet?.idleRobots || 0}</span>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: '#94a3b8' }}>Maintenance</span>
              <span style={{ color: '#dc2626' }}>{client.fleet?.maintenanceRobots || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientDetail;
