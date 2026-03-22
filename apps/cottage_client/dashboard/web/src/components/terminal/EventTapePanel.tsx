import { Panel } from './Panel'
import type { EventItem } from './types'

export function EventTapePanel({ events }: { events: EventItem[] }) {
  return (
    <Panel title="Event Tape" meta={`${events.length} recent`}>
      <div className="event-list">
        {events.map((item) => (
          <div className={`event-row event-row--${item.tone}`} key={item.id}>
            <div className="event-row__time">{item.time}</div>
            <div className="event-row__body">
              <strong>{item.entity}</strong>
              <span>{item.message}</span>
            </div>
          </div>
        ))}
      </div>
    </Panel>
  )
}
