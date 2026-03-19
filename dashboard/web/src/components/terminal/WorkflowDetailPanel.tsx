import { AssetGlyph, robotTypeLabel } from './AssetGlyph'
import { Panel } from './Panel'
import type { Asset, ScenarioState, TaskItem, WorkflowStage } from './types'

type Props = {
  assets: Asset[]
  task: TaskItem
  stages: WorkflowStage[]
  scenario: ScenarioState
}

export function WorkflowDetailPanel({ assets, task, stages, scenario }: Props) {
  const ownerAsset = assets.find((asset) => asset.label === task.owner || asset.id === task.owner)

  return (
    <Panel title="Workflow Detail" meta={task.id}>
      <div className="detail-stack">
        <div className="detail-row"><span>Summary</span><strong>{task.summary}</strong></div>
        <div className="detail-row"><span>Route</span><strong>{task.route}</strong></div>
        <div className="detail-row">
          <span>Owner</span>
          <strong className="detail-owner">
            {ownerAsset ? <AssetGlyph asset={ownerAsset} size="sm" /> : null}
            <span>{task.owner}</span>
            {ownerAsset ? <em>{robotTypeLabel(ownerAsset)}</em> : null}
          </strong>
        </div>
        <div className="detail-row"><span>Stage</span><strong>{task.stage.replace('_', ' ')}</strong></div>
        <div className="detail-row"><span>ETA</span><strong>{task.eta}</strong></div>
      </div>
      <div className={`scenario-banner scenario-banner--${scenario.status}`}>
        <strong>{scenario.name}</strong>
        <span>{scenario.message}</span>
      </div>
      <div className="workflow-rail">
        {stages.map((stage) => (
          <div
            className={`workflow-step${stage.complete ? ' is-complete' : ''}${stage.active ? ' is-active' : ''}`}
            key={stage.label}
          >
            <span className="workflow-step__dot" />
            <span>{stage.label}</span>
          </div>
        ))}
      </div>
    </Panel>
  )
}
