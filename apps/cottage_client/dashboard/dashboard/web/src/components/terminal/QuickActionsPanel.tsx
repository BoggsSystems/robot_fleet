import { Play, BellRing, PauseCircle, History } from 'lucide-react'
import { Panel } from './Panel'
import type { TaskItem } from './types'

type Props = {
  onReplay: () => void
  onStartScenario: () => void
  onAcknowledge: () => void
  onPause: () => void
  onPauseMission: () => void
  onResumeMission: () => void
  onRetryMission: () => void
  onPreviewReplan: () => void
  onApplyReplan: () => void
  onFailTask: () => void
  selectedTask?: TaskItem
}

export function QuickActionsPanel({
  onReplay,
  onStartScenario,
  onAcknowledge,
  onPause,
  onPauseMission,
  onResumeMission,
  onRetryMission,
  onPreviewReplan,
  onApplyReplan,
  onFailTask,
  selectedTask,
}: Props) {
  const actions = [
    { label: 'Replay Run', icon: History, onClick: onReplay },
    { label: 'Start Scenario', icon: Play, onClick: onStartScenario },
    { label: 'Acknowledge', icon: BellRing, onClick: onAcknowledge },
    { label: 'Pause Queue', icon: PauseCircle, onClick: onPause },
    ...(selectedTask?.missionId
      ? selectedTask.missionStatus === 'paused'
        ? [{ label: 'Resume Mission', icon: Play, onClick: onResumeMission }]
        : [{ label: 'Pause Mission', icon: PauseCircle, onClick: onPauseMission }]
      : []),
    ...(selectedTask?.missionStatus === 'blocked'
      ? selectedTask.replanAvailable
        ? [{ label: 'Apply Replan', icon: Play, onClick: onApplyReplan }]
        : [{ label: 'Preview Replan', icon: History, onClick: onPreviewReplan }]
      : []),
    ...(selectedTask?.missionStatus === 'blocked'
      ? [{ label: 'Retry Mission', icon: History, onClick: onRetryMission }]
      : []),
    ...(selectedTask?.stage === 'assigned' || selectedTask?.stage === 'in_transit'
      ? [{ label: 'Mark Failed', icon: BellRing, onClick: onFailTask }]
      : []),
  ]

  return (
    <Panel
      title="Quick Actions"
      meta={
        selectedTask?.missionId
          ? selectedTask.blockedReason
            ? selectedTask.replanSummary ?? `Fallback ${selectedTask.fallbackRobotIds?.length ? 'available' : 'unavailable'}`
            : `Mission ${selectedTask.missionStatus ?? 'active'}`
          : 'Scenario controls'
      }
    >
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
