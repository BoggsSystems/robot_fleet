import { Panel } from './Panel'
import type { CommandLogEntry } from './types'

type Props = {
  items: CommandLogEntry[]
}

export function CommandLogPanel({ items }: Props) {
  return (
    <Panel title="Command Log" meta={`${items.length} entries`}>
      <div className="command-log">
        {items.map((item) => (
          <div key={item.id} className="command-row">
            <div className="command-row__head">
              <strong>{item.action}</strong>
              <span className={`command-status command-status--${item.status}`}>{item.status}</span>
            </div>
            <div className="command-row__meta">
              <span>{item.target}</span>
              <span>{item.time}</span>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
