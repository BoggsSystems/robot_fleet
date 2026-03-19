import { Play, BellRing, PauseCircle, History } from 'lucide-react'
import { Panel } from './Panel'

type Props = {
  onReplay: () => void
  onStartScenario: () => void
  onAcknowledge: () => void
  onPause: () => void
}

export function QuickActionsPanel({ onReplay, onStartScenario, onAcknowledge, onPause }: Props) {
  const actions = [
    { label: 'Replay Run', icon: History, onClick: onReplay },
    { label: 'Start Scenario', icon: Play, onClick: onStartScenario },
    { label: 'Acknowledge', icon: BellRing, onClick: onAcknowledge },
    { label: 'Pause Queue', icon: PauseCircle, onClick: onPause },
  ]

  return (
    <Panel title="Quick Actions" meta="Scenario controls">
      <div className="action-grid">
        {actions.map((action) => {
          const Icon = action.icon
          return (
            <button className="action-button" key={action.label} onClick={action.onClick}>
              <Icon size={14} />
              {action.label}
            </button>
          )
        })}
      </div>
    </Panel>
  )
}
