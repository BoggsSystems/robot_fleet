import { Panel } from './Panel'
import type { TelemetryItem } from './types'

export function TelemetryStrip({ items }: { items: TelemetryItem[] }) {
  return (
    <section className="telemetry-strip">
      {items.map((item) => (
        <Panel key={item.label} title={item.label} meta={item.delta} compact>
          <div className={`telemetry-value telemetry-value--${item.tone}`}>{item.value}</div>
        </Panel>
      ))}
    </section>
  )
}
