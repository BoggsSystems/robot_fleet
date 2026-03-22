import { Panel } from './Panel'
import type { ReplayState, ScenarioState } from './types'

type Props = {
  replay: ReplayState
  scenario: ScenarioState
}

export function ReplayPanel({ replay, scenario }: Props) {
  return (
    <Panel title="Replay Context" meta={replay.mode.toUpperCase()}>
      <div className="replay-stack">
        <div className="replay-row">
          <span>Cursor</span>
          <strong>{replay.cursorLabel}</strong>
        </div>
        <div className="replay-row">
          <span>Scenario</span>
          <strong>{scenario.name}</strong>
        </div>
        <div className="replay-row">
          <span>State</span>
          <strong>{scenario.status}</strong>
        </div>
        <div className="replay-row">
          <span>Last action</span>
          <strong>{replay.lastAction}</strong>
        </div>
        <div className="replay-progress">
          <div className="replay-progress__bar" style={{ width: `${replay.progressPct}%` }} />
        </div>
      </div>
    </Panel>
  )
}
