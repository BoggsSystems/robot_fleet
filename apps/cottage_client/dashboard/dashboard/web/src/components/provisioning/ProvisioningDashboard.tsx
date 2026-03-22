import { useState, useEffect } from 'react';
import { Package, Truck, CheckCircle, AlertCircle, Box, Search, Filter, ChevronRight, RotateCcw } from 'lucide-react';
import './ProvisioningDashboard.css';

export type ProvisioningStatus = 
  | 'ordered'           // Ordered from supplier
  | 'in_warehouse'      // Received, waiting for provisioning
  | 'provisioning'      // Currently being onboarded
  | 'ready_to_ship'     // Pre-configured, in inventory
  | 'shipped'           // In transit to client
  | 'deployed'          // Active at client site
  | 'maintenance'       // Returned for repair
  | 'retired';          // End of life

export type ProvisioningRecord = {
  id: string;
  serialNumber: string;
  robotType: string;
  robotCategory: string;
  status: ProvisioningStatus;
  clientId?: string;
  clientName?: string;
  fleetId?: string;
  fleetName?: string;
  orderDate?: string;
  receivedDate?: string;
  provisionedDate?: string;
  shippedDate?: string;
  deployedDate?: string;
  notes: string;
  firmwareVersion: string;
  hardwareVersion: string;
};

interface ProvisioningDashboardProps {
  onSelectRobot?: (robot: ProvisioningRecord) => void;
  onCancel?: () => void;
}

const DEFAULT_INVENTORY: ProvisioningRecord[] = [
  {
    id: 'inv_1',
    serialNumber: 'U1R1-2403-001',
    robotType: 'unitree_r1',
    robotCategory: 'Humanoid',
    status: 'ready_to_ship',
    clientId: 'client_1',
    clientName: 'Acme Distribution',
    fleetId: 'fleet_1',
    fleetName: 'Warehouse Alpha',
    receivedDate: '2024-03-01',
    provisionedDate: '2024-03-02',
    notes: 'Pre-configured for Acme - Heavy Lifter One',
    firmwareVersion: 'v2.1.4',
    hardwareVersion: 'R1-B',
  },
  {
    id: 'inv_2',
    serialNumber: 'U1G1-2403-015',
    robotType: 'unitree_g1',
    robotCategory: 'Humanoid',
    status: 'provisioning',
    clientId: 'client_2',
    clientName: 'TechStart Inc',
    receivedDate: '2024-03-10',
    notes: 'Running calibration for TechStart',
    firmwareVersion: 'v2.1.4',
    hardwareVersion: 'G1-A',
  },
  {
    id: 'inv_3',
    serialNumber: 'U1G2-2403-042',
    robotType: 'unitree_go2',
    robotCategory: 'Quadruped',
    status: 'in_warehouse',
    receivedDate: '2024-03-15',
    notes: 'Awaiting client assignment',
    firmwareVersion: 'v2.0.8',
    hardwareVersion: 'Go2-Pro',
  },
  {
    id: 'inv_4',
    serialNumber: 'U1R1-2403-003',
    robotType: 'unitree_r1',
    robotCategory: 'Humanoid',
    status: 'deployed',
    clientId: 'client_1',
    clientName: 'Acme Distribution',
    fleetId: 'fleet_1',
    fleetName: 'Warehouse Alpha',
    receivedDate: '2024-02-20',
    provisionedDate: '2024-02-21',
    shippedDate: '2024-02-22',
    deployedDate: '2024-02-23',
    notes: 'Heavy Lifter Two - operational',
    firmwareVersion: 'v2.1.4',
    hardwareVersion: 'R1-B',
  },
];

const STATUS_CONFIG: Record<ProvisioningStatus, { label: string; color: string; icon: any }> = {
  ordered: { label: 'Ordered', color: '#71717a', icon: Package },
  in_warehouse: { label: 'In Warehouse', color: '#f59e0b', icon: Box },
  provisioning: { label: 'Provisioning', color: '#3b82f6', icon: RotateCcw },
  ready_to_ship: { label: 'Ready to Ship', color: '#8b5cf6', icon: CheckCircle },
  shipped: { label: 'Shipped', color: '#06b6d4', icon: Truck },
  deployed: { label: 'Deployed', color: '#10b981', icon: CheckCircle },
  maintenance: { label: 'Maintenance', color: '#ef4444', icon: AlertCircle },
  retired: { label: 'Retired', color: '#6b7280', icon: Box },
};

export function ProvisioningDashboard({ onSelectRobot: _onSelectRobot, onCancel }: ProvisioningDashboardProps) {
  const [inventory, setInventory] = useState<ProvisioningRecord[]>([]);
  const [filter, setFilter] = useState<ProvisioningStatus | 'all'>('all');
  const [search, setSearch] = useState('');
  const [selectedRobot, setSelectedRobot] = useState<ProvisioningRecord | null>(null);

  useEffect(() => {
    const stored = localStorage.getItem('inventory');
    if (stored) {
      setInventory(JSON.parse(stored));
    } else {
      setInventory(DEFAULT_INVENTORY);
      localStorage.setItem('inventory', JSON.stringify(DEFAULT_INVENTORY));
    }
  }, []);

  const getStatusStats = () => {
    const stats: Record<string, number> = {};
    inventory.forEach(item => {
      stats[item.status] = (stats[item.status] || 0) + 1;
    });
    return stats;
  };

  const stats = getStatusStats();

  const filteredInventory = inventory.filter(item => {
    const matchesFilter = filter === 'all' || item.status === filter;
    const matchesSearch = 
      item.serialNumber.toLowerCase().includes(search.toLowerCase()) ||
      item.robotType.toLowerCase().includes(search.toLowerCase()) ||
      item.clientName?.toLowerCase().includes(search.toLowerCase()) ||
      item.notes.toLowerCase().includes(search.toLowerCase());
    return matchesFilter && matchesSearch;
  });

  const getTypeIcon = (category: string) => {
    switch (category) {
      case 'Humanoid': return '🤖';
      case 'Quadruped': return '🐕';
      case 'Wheeled': return '🔄';
      default: return '⚙️';
    }
  };

  return (
    <div className="provisioning-dashboard">
      <div className="prov-header">
        <div>
          <h2>Provisioning & Fulfillment</h2>
          <p>Track robot inventory from warehouse to deployment</p>
        </div>
        <div className="prov-stats">
          <div className="stat-card">
            <span className="stat-value">{inventory.length}</span>
            <span className="stat-label">Total Units</span>
          </div>
          <div className="stat-card highlight">
            <span className="stat-value">{stats.ready_to_ship || 0}</span>
            <span className="stat-label">Ready to Ship</span>
          </div>
          <div className="stat-card">
            <span className="stat-value">{stats.deployed || 0}</span>
            <span className="stat-label">Deployed</span>
          </div>
        </div>
      </div>

      {/* Status Pipeline */}
      <div className="status-pipeline">
        {(['ordered', 'in_warehouse', 'provisioning', 'ready_to_ship', 'shipped', 'deployed'] as ProvisioningStatus[]).map(status => {
          const config = STATUS_CONFIG[status];
          const count = stats[status] || 0;
          const isActive = filter === status;
          return (
            <button
              key={status}
              className={`pipeline-stage ${isActive ? 'active' : ''}`}
              onClick={() => setFilter(isActive ? 'all' : status)}
            >
              <div className="stage-icon" style={{ color: config.color }}>
                <config.icon size={20} />
              </div>
              <div className="stage-info">
                <span className="stage-count">{count}</span>
                <span className="stage-label">{config.label}</span>
              </div>
            </button>
          );
        })}
      </div>

      {/* Search & Filter */}
      <div className="prov-toolbar">
        <div className="search-box">
          <Search size={18} />
          <input
            type="text"
            placeholder="Search by serial, type, client, or notes..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <button className="btn-filter">
          <Filter size={18} />
          More Filters
        </button>
      </div>

      {/* Inventory Table */}
      <div className="inventory-table-container">
        <table className="inventory-table">
          <thead>
            <tr>
              <th>Serial Number</th>
              <th>Type</th>
              <th>Status</th>
              <th>Client</th>
              <th>Fleet</th>
              <th>Received</th>
              <th>Shipped</th>
              <th>Firmware</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredInventory.map(item => {
              const statusConfig = STATUS_CONFIG[item.status];
              return (
                <tr 
                  key={item.id} 
                  className="inventory-row"
                  onClick={() => setSelectedRobot(item)}
                >
                  <td className="serial-cell">
                    <code>{item.serialNumber}</code>
                  </td>
                  <td className="type-cell">
                    <span className="type-icon">{getTypeIcon(item.robotCategory)}</span>
                    <span className="type-name">{item.robotType}</span>
                  </td>
                  <td>
                    <span 
                      className="status-pill" 
                      style={{ 
                        backgroundColor: `${statusConfig.color}20`,
                        color: statusConfig.color,
                        borderColor: statusConfig.color
                      }}
                    >
                      <statusConfig.icon size={12} />
                      {statusConfig.label}
                    </span>
                  </td>
                  <td>{item.clientName || '—'}</td>
                  <td>{item.fleetName || '—'}</td>
                  <td>{item.receivedDate || '—'}</td>
                  <td>{item.shippedDate || '—'}</td>
                  <td><code className="firmware">{item.firmwareVersion}</code></td>
                  <td>
                    <button className="btn-action">
                      View <ChevronRight size={14} />
                    </button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Detail Modal */}
      {selectedRobot && (
        <div className="robot-detail-overlay" onClick={() => setSelectedRobot(null)}>
          <div className="robot-detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="detail-header">
              <div className="detail-title">
                <span className="detail-icon">{getTypeIcon(selectedRobot.robotCategory)}</span>
                <div>
                  <h3>{selectedRobot.serialNumber}</h3>
                  <p>{selectedRobot.robotType} • {selectedRobot.robotCategory}</p>
                </div>
              </div>
              <button className="btn-close" onClick={() => setSelectedRobot(null)}>
                ×
              </button>
            </div>

            <div className="detail-content">
              <div className="detail-section">
                <h4>Status</h4>
                <div className="status-timeline">
                  {(['ordered', 'in_warehouse', 'provisioning', 'ready_to_ship', 'shipped', 'deployed'] as ProvisioningStatus[]).map((status, idx) => {
                    const config = STATUS_CONFIG[status];
                    const isComplete = ['ordered', 'in_warehouse', 'provisioning', 'ready_to_ship', 'shipped', 'deployed'].indexOf(selectedRobot.status) >= idx;
                    const isCurrent = selectedRobot.status === status;
                    
                    return (
                      <div 
                        key={status} 
                        className={`timeline-item ${isComplete ? 'complete' : ''} ${isCurrent ? 'current' : ''}`}
                      >
                        <div className="timeline-dot" style={{ color: isComplete ? config.color : '#3f3f5f' }}>
                          <config.icon size={16} />
                        </div>
                        <span className="timeline-label">{config.label}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              <div className="detail-section">
                <h4>Assignment</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Client</label>
                    <span>{selectedRobot.clientName || 'Unassigned'}</span>
                  </div>
                  <div className="detail-item">
                    <label>Fleet</label>
                    <span>{selectedRobot.fleetName || 'Unassigned'}</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Technical</h4>
                <div className="detail-grid">
                  <div className="detail-item">
                    <label>Firmware</label>
                    <code>{selectedRobot.firmwareVersion}</code>
                  </div>
                  <div className="detail-item">
                    <label>Hardware</label>
                    <span>{selectedRobot.hardwareVersion}</span>
                  </div>
                </div>
              </div>

              <div className="detail-section">
                <h4>Notes</h4>
                <p className="detail-notes">{selectedRobot.notes || 'No notes'}</p>
              </div>
            </div>

            <div className="detail-actions">
              <button className="btn-secondary" onClick={() => setSelectedRobot(null)}>
                Close
              </button>
              {selectedRobot.status === 'ready_to_ship' && (
                <button className="btn-primary">
                  <Truck size={16} />
                  Mark as Shipped
                </button>
              )}
              {selectedRobot.status === 'in_warehouse' && (
                <button className="btn-primary">
                  <RotateCcw size={16} />
                  Start Provisioning
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {onCancel && (
        <div className="prov-footer">
          <button className="btn-secondary" onClick={onCancel}>
            Back to Dashboard
          </button>
        </div>
      )}
    </div>
  );
}
