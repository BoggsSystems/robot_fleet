import { Radio, MapPinned } from 'lucide-react'
import { AssetGlyph } from './AssetGlyph'
import { Panel } from './Panel'
import type { Asset, GraphNode, TaskItem } from './types'

type Props = {
  assets: Asset[]
  nodes: GraphNode[]
  links: readonly (readonly [string, string])[]
  selectedNodeId: string
  selectedTask: TaskItem
  onSelectNode: (nodeId: string) => void
}

export function PropertyTwinPanel({ assets, nodes, links, selectedNodeId, selectedTask, onSelectNode }: Props) {
  const activeRoute = new Set(selectedTask.routeNodeIds)
  const assetsByNode = new Map<string, Asset[]>()
  for (const asset of assets) {
    const existing = assetsByNode.get(asset.locationNodeId) ?? []
    existing.push(asset)
    assetsByNode.set(asset.locationNodeId, existing)
  }

  return (
    <Panel title="Property Twin" meta="Placeholder site graph">
      <div className="map-shell">
        <div className="map-grid">
          {links.map(([from, to]) => {
            const active = activeRoute.has(from) && activeRoute.has(to)
            return (
              <div
                className={`map-link map-link--${from} map-link--${to}${active ? ' map-link--active' : ''}`}
                key={`${from}-${to}`}
              />
            )
          })}
          {nodes.map((node) => (
            <button
              key={node.id}
              className={`map-node map-node--${node.state}${node.id === selectedNodeId ? ' is-selected' : ''}${activeRoute.has(node.id) ? ' is-on-route' : ''}`}
              style={{ gridColumn: node.col, gridRow: node.row }}
              onClick={() => onSelectNode(node.id)}
            >
              <span className="map-node__label">{node.label}</span>
              <span className="map-node__icon">
                {node.id === 'landing' ? <Radio size={12} /> : null}
                {node.type === 'room' ? <MapPinned size={12} /> : null}
              </span>
              <span className="map-node__assets">
                {(assetsByNode.get(node.id) ?? []).slice(0, 3).map((asset) => (
                  <AssetGlyph key={asset.id} asset={asset} size="sm" />
                ))}
              </span>
            </button>
          ))}
        </div>

        <div className="map-legend">
          <span><span className="status-dot status-active" /> live asset movement</span>
          <span><span className="status-dot status-idle" /> available location</span>
          <span><span className="status-dot status-warning" /> attention area</span>
        </div>
      </div>
    </Panel>
  )
}
