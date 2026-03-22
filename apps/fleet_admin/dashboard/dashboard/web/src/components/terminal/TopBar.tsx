import { Activity, AlertTriangle, Cloud, LogOut, Search, User, Users } from 'lucide-react'
import type { SessionUser } from '../../auth/AuthProvider'
import type { ScenarioState } from './types'

type TopBarProps = {
  user: SessionUser | null
  onLogout: () => void
  runtimeLabel: string
  scenario: ScenarioState
  alertCount: number
  onSwitchView?: () => void
  currentView?: 'terminal' | 'customer-onboarding'
}

export function TopBar({ user, onLogout, runtimeLabel, scenario, alertCount, onSwitchView, currentView }: TopBarProps) {
  return (
    <header className="terminal-topbar">
      <div className="topbar-left">
        <div className="brand-lockup">
          <span className="brand-mark">CT</span>
          <div>
            <h1>Cottage</h1>
            <p>Operations Terminal</p>
          </div>
        </div>
        <span className="env-badge">{runtimeLabel}</span>
      </div>

      <div className="topbar-center">
        <div className="summary-chip"><Activity size={14} /> {scenario.status === 'running' ? scenario.name : 'Scenario ready'}</div>
        <div className="summary-chip"><AlertTriangle size={14} /> {alertCount} open alerts</div>
        <div className="summary-chip"><Cloud size={14} /> Light wind / clear</div>
        {onSwitchView && (
          <button className="summary-chip view-switcher" onClick={onSwitchView}>
            <Users size={14} /> {currentView === 'terminal' ? 'Customer Admin' : 'Terminal'}
          </button>
        )}
      </div>

      <div className="topbar-right">
        <div className="search-shell">
          <Search size={14} />
          <input value="carrier-01" readOnly />
        </div>
        <div className="user-chip"><User size={14} /> {user?.displayName ?? 'Operator'}</div>
        <button className="ghost-button" onClick={onLogout}><LogOut size={14} /> Logout</button>
      </div>
    </header>
  )
}
