import { AssetGlyph, robotTypeLabel } from './AssetGlyph'
import { Panel } from './Panel'
import type { Asset, TaskItem } from './types'

type Props = {
  assets: Asset[]
  tasks: TaskItem[]
  selectedTaskId: string
  onSelect: (taskId: string) => void
}

export function TaskQueuePanel({ assets, tasks, selectedTaskId, onSelect }: Props) {
  return (
    <Panel title="Task Queue" meta={`${tasks.length} staged`}>
      <div className="task-list">
        {tasks.map((task) => {
          const ownerAsset = assets.find((asset) => asset.label === task.owner || asset.id === task.owner)
          return (
            <button
              key={task.id}
              className={`task-row${task.id === selectedTaskId ? ' is-selected' : ''}`}
              onClick={() => onSelect(task.id)}
            >
              <div className="task-row__header">
                <strong>{task.summary}</strong>
                <span className={`task-stage task-stage--${task.stage}`}>{task.stage.replace('_', ' ')}</span>
              </div>
              <div className="task-row__meta">
                <span>{task.route}</span>
                <span className="task-row__owner">
                  {ownerAsset ? <AssetGlyph asset={ownerAsset} size="sm" /> : null}
                  <span>{task.owner}</span>
                  {ownerAsset ? <em>{robotTypeLabel(ownerAsset)}</em> : null}
                </span>
              </div>
              <div className="task-row__footer">
                <span className="task-row__eta">ETA {task.eta}</span>
              </div>
            </button>
          )
        })}
      </div>
    </Panel>
  )
}
