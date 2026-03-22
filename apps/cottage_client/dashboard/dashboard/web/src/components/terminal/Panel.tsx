import type { ReactNode } from 'react'

type PanelProps = {
  title: string
  meta?: string
  compact?: boolean
  children: ReactNode
}

export function Panel({ title, meta, compact = false, children }: PanelProps) {
  return (
    <section className={`terminal-panel${compact ? ' terminal-panel--compact' : ''}`}>
      <header className="terminal-panel__header">
        <p className="eyebrow">{title}</p>
        {meta ? <span className="panel-meta">{meta}</span> : null}
      </header>
      <div className="terminal-panel__body">{children}</div>
    </section>
  )
}
