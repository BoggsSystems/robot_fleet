import { Panel } from './Panel'
import type { AlertItem } from './types'

export function AlertsPanel({ alerts }: { alerts: AlertItem[] }) {
  return (
    <Panel title="Alerts" meta={`${alerts.length} open`}>
      <div className="alert-list">
        {alerts.map((alert) => (
          <div className={`alert-row alert-row--${alert.severity}`} key={alert.id}>
            <div className="alert-row__top">
              <strong>{alert.area}</strong>
              <span>{alert.time}</span>
            </div>
            <p>{alert.message}</p>
          </div>
        ))}
      </div>
    </Panel>
  )
}
