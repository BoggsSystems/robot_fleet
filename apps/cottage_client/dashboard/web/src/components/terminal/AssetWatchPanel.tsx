import { Battery } from 'lucide-react'
import { AssetGlyph, robotTypeLabel } from './AssetGlyph'
import { Panel } from './Panel'
import type { Asset } from './types'

type Props = {
  assets: Asset[]
  selectedAssetId: string
  onSelect: (assetId: string) => void
}

export function AssetWatchPanel({ assets, selectedAssetId, onSelect }: Props) {
  return (
    <Panel title="Asset Watch" meta={`${assets.length} tracked`}>
      <div className="asset-list">
        {assets.map((asset) => {
          return (
            <button
              key={asset.id}
              className={`asset-row${asset.id === selectedAssetId ? ' is-selected' : ''}`}
              onClick={() => onSelect(asset.id)}
            >
              <div className="asset-row__head">
                <div className="asset-row__identity">
                  <span className={`status-dot status-${asset.status}`} />
                  <AssetGlyph asset={asset} />
                  <div className="asset-row__identity-copy">
                    <strong>{asset.label}</strong>
                    <span className="asset-model">{asset.model ?? robotTypeLabel(asset)}</span>
                  </div>
                </div>
                <span className={`asset-kind asset-kind--${asset.robotType ?? asset.kind}`}>{robotTypeLabel(asset)}</span>
              </div>
              <div className="asset-row__meta">
                <span>{asset.location}</span>
                <span>{asset.task}</span>
              </div>
              <div className="asset-row__footer">
                {typeof asset.battery === 'number' ? (
                  <div className="asset-row__metric">
                    <Battery size={13} />
                    <span>{asset.battery}%</span>
                  </div>
                ) : <span className="asset-row__metric-placeholder">No battery feed</span>}
                <span className="asset-eta">{asset.eta}</span>
              </div>
            </button>
          )
        })}
      </div>
    </Panel>
  )
}
