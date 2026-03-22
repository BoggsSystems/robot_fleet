import type { StatusCell } from './types'

export function StatusStrip({ items }: { items: StatusCell[] }) {
  return (
    <section className="status-strip">
      {items.map((item) => (
        <div className="status-cell" key={item.label}>
          <span>{item.label}</span>
          <strong>{item.value}</strong>
        </div>
      ))}
    </section>
  )
}
