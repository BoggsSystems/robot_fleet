import { AssetGlyph, robotTypeLabel } from './AssetGlyph'
import { Panel } from './Panel'
import type { Asset, GraphNode, TaskItem } from './types'

type Props = {
  asset: Asset
  node?: GraphNode
  task?: TaskItem
}

export function TwinInspectorPanel({ asset, node, task }: Props) {
  return (
    <Panel title="Twin Inspector" meta={asset.id}>
      <div className="detail-stack">
        <div className="detail-row">
          <span>Asset</span>
          <strong className="detail-owner">
            <AssetGlyph asset={asset} size="sm" />
            <span>{asset.label}</span>
          </strong>
        </div>
        <div className="detail-row"><span>Kind</span><strong>{asset.kind}</strong></div>
        <div className="detail-row"><span>Robot type</span><strong>{robotTypeLabel(asset)}</strong></div>
        <div className="detail-row"><span>Model</span><strong>{asset.model ?? 'Unspecified'}</strong></div>
        <div className="detail-row"><span>Status</span><strong>{asset.status}</strong></div>
        <div className="detail-row"><span>Location</span><strong>{asset.location}</strong></div>
        <div className="detail-row"><span>Task</span><strong>{asset.task ?? 'None'}</strong></div>
        <div className="detail-row"><span>Selected node</span><strong>{node?.label ?? 'Unbound'}</strong></div>
        <div className="detail-row"><span>Node state</span><strong>{node?.state ?? 'Unknown'}</strong></div>
        <div className="detail-row"><span>Route binding</span><strong>{task?.route ?? 'No active route'}</strong></div>
        <div className="detail-row"><span>ETA</span><strong>{task?.eta ?? asset.eta ?? 'N/A'}</strong></div>
      </div>
    </Panel>
  )
}
