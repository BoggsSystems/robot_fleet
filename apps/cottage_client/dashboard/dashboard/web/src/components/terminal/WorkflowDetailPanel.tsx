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
        {task.stepIndex && task.totalSteps ? <div className="detail-row"><span>Step</span><strong>{task.stepIndex} / {task.totalSteps}</strong></div> : null}
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
        {task.dependsOn?.length ? <div className="detail-row"><span>Depends On</span><strong>{task.dependsOn.join(', ')}</strong></div> : null}
        {task.approvalRequired ? <div className="detail-row"><span>Approval</span><strong>{task.approvalStatus?.replace('_', ' ') ?? 'pending'}</strong></div> : null}
        {task.assignmentRationale ? <div className="detail-row"><span>Assignment</span><strong>{task.assignmentRationale}</strong></div> : null}
        {task.fallbackRobotIds?.length ? <div className="detail-row"><span>Fallback</span><strong>{task.fallbackRobotIds.join(', ')}</strong></div> : null}
        {task.blockedReason ? <div className="detail-row"><span>Blocked Reason</span><strong>{task.blockedReason}</strong></div> : null}
        {task.proposalWarnings?.length ? <div className="detail-row"><span>Proposal Warnings</span><strong>{task.proposalWarnings.join(' | ')}</strong></div> : null}
        {task.validatedWarnings?.length ? <div className="detail-row"><span>Validated Warnings</span><strong>{task.validatedWarnings.join(' | ')}</strong></div> : null}
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
