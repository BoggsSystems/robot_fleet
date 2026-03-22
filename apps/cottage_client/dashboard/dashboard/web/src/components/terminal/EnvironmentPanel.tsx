import { Panel } from './Panel'

export function EnvironmentPanel() {
  return (
    <Panel title="Environment" meta="Site summary">
      <div className="detail-stack">
        <div className="detail-row"><span>Weather</span><strong>Clear / 8°C</strong></div>
        <div className="detail-row"><span>Wind</span><strong>12 km/h SW</strong></div>
        <div className="detail-row"><span>Dock</span><strong>Open transfer window</strong></div>
        <div className="detail-row"><span>Water</span><strong>Low chop</strong></div>
        <div className="detail-row"><span>Path</span><strong>Dry surface</strong></div>
        <div className="detail-row"><span>Network</span><strong>Mesh stable</strong></div>
      </div>
    </Panel>
  )
}
