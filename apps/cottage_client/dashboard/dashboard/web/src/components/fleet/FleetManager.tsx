import { useState, useEffect } from 'react';
import { Plus, Edit2, Trash2, Users, MapPin, X, ChevronRight } from 'lucide-react';
import type { Fleet } from '../onboarding/OnboardingWizard';
import './FleetManager.css';

interface FleetManagerProps {
  onSelectFleet?: (fleet: Fleet) => void;
  onCancel?: () => void;
  selectable?: boolean;
}

const DEFAULT_FLEETS: Fleet[] = [
  {
    id: 'default',
    name: 'Main Fleet',
    description: 'Default fleet for all robots',
    location: 'Warehouse A',
    robotCount: 0,
    createdAt: new Date().toISOString(),
  },
];

export function FleetManager({ onSelectFleet, onCancel, selectable = false }: FleetManagerProps) {
  const [fleets, setFleets] = useState<Fleet[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingFleet, setEditingFleet] = useState<Fleet | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '', location: '' });

  // Load fleets from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem('fleets');
    if (stored) {
      setFleets(JSON.parse(stored));
    } else {
      setFleets(DEFAULT_FLEETS);
      localStorage.setItem('fleets', JSON.stringify(DEFAULT_FLEETS));
    }
  }, []);

  const saveFleets = (newFleets: Fleet[]) => {
    setFleets(newFleets);
    localStorage.setItem('fleets', JSON.stringify(newFleets));
  };

  const handleCreate = () => {
    if (!formData.name.trim()) return;

    const newFleet: Fleet = {
      id: `fleet_${Date.now()}`,
      name: formData.name,
      description: formData.description,
      location: formData.location,
      robotCount: 0,
      createdAt: new Date().toISOString(),
    };

    saveFleets([...fleets, newFleet]);
    setFormData({ name: '', description: '', location: '' });
    setShowCreateForm(false);
  };

  const handleUpdate = () => {
    if (!editingFleet || !formData.name.trim()) return;

    const updated = fleets.map(f =>
      f.id === editingFleet.id
        ? { ...f, name: formData.name, description: formData.description, location: formData.location }
        : f
    );

    saveFleets(updated);
    setEditingFleet(null);
    setFormData({ name: '', description: '', location: '' });
  };

  const handleDelete = (fleetId: string) => {
    if (!confirm('Are you sure you want to delete this fleet? Robots in this fleet will become unassigned.')) return;
    saveFleets(fleets.filter(f => f.id !== fleetId));
  };

  const startEdit = (fleet: Fleet) => {
    setEditingFleet(fleet);
    setFormData({
      name: fleet.name,
      description: fleet.description,
      location: fleet.location,
    });
  };

  return (
    <div className="fleet-manager">
      <div className="fleet-header">
        <h2>Fleet Management</h2>
        <p>Create and manage robot fleets</p>
      </div>

      {/* Fleet List */}
      <div className="fleet-list">
        {fleets.map(fleet => (
          <div
            key={fleet.id}
            className={`fleet-card ${selectable ? 'selectable' : ''}`}
            onClick={() => selectable && onSelectFleet?.(fleet)}
          >
            <div className="fleet-info">
              <div className="fleet-icon">
                {fleet.id === 'default' ? '🏭' : '🚀'}
              </div>
              <div className="fleet-details">
                <h4>{fleet.name}</h4>
                <p>{fleet.description || 'No description'}</p>
                <div className="fleet-meta">
                  <span><MapPin size={12} /> {fleet.location || 'Unknown location'}</span>
                  <span><Users size={12} /> {fleet.robotCount} robots</span>
                </div>
              </div>
            </div>

            {!selectable && (
              <div className="fleet-actions">
                <button
                  className="btn-icon"
                  onClick={(e) => { e.stopPropagation(); startEdit(fleet); }}
                >
                  <Edit2 size={16} />
                </button>
                {fleet.id !== 'default' && (
                  <button
                    className="btn-icon delete"
                    onClick={(e) => { e.stopPropagation(); handleDelete(fleet.id); }}
                  >
                    <Trash2 size={16} />
                  </button>
                )}
              </div>
            )}

            {selectable && (
              <ChevronRight size={20} className="select-arrow" />
            )}
          </div>
        ))}
      </div>

      {/* Create New Fleet Button */}
      {!showCreateForm && !editingFleet && !selectable && (
        <button className="btn-create-fleet" onClick={() => setShowCreateForm(true)}>
          <Plus size={20} />
          Create New Fleet
        </button>
      )}

      {/* Create/Edit Form */}
      {(showCreateForm || editingFleet) && (
        <div className="fleet-form-overlay">
          <div className="fleet-form">
            <div className="form-header">
              <h3>{editingFleet ? 'Edit Fleet' : 'Create New Fleet'}</h3>
              <button
                className="btn-close"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingFleet(null);
                  setFormData({ name: '', description: '', location: '' });
                }}
              >
                <X size={20} />
              </button>
            </div>

            <div className="form-fields">
              <div className="form-field">
                <label>Fleet Name *</label>
                <input
                  type="text"
                  placeholder="e.g., Warehouse Fleet"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Description</label>
                <input
                  type="text"
                  placeholder="What is this fleet for?"
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>

              <div className="form-field">
                <label>Location</label>
                <input
                  type="text"
                  placeholder="e.g., Building A, Floor 2"
                  value={formData.location}
                  onChange={(e) => setFormData({ ...formData, location: e.target.value })}
                />
              </div>
            </div>

            <div className="form-actions">
              <button
                className="btn-secondary"
                onClick={() => {
                  setShowCreateForm(false);
                  setEditingFleet(null);
                  setFormData({ name: '', description: '', location: '' });
                }}
              >
                Cancel
              </button>
              <button
                className="btn-primary"
                onClick={editingFleet ? handleUpdate : handleCreate}
                disabled={!formData.name.trim()}
              >
                {editingFleet ? 'Update Fleet' : 'Create Fleet'}
              </button>
            </div>
          </div>
        </div>
      )}

      {onCancel && (
        <div className="fleet-actions-footer">
          <button className="btn-secondary" onClick={onCancel}>
            Cancel
          </button>
        </div>
      )}
    </div>
  );
}
