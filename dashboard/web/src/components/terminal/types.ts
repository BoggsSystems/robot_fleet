export type AssetKind = 'robot' | 'boat' | 'cargo'
export type RobotType = 'quadruped' | 'humanoid' | 'drone' | 'boat' | 'cargo' | 'unknown'

export type AssetStatus = 'idle' | 'active' | 'warning' | 'maintenance'

export type TaskStage = 'queued' | 'assigned' | 'in_transit' | 'completed'

export type AlertSeverity = 'info' | 'warn' | 'fault'

export type EventTone = 'live' | 'ok' | 'warn'

export type Asset = {
  id: string
  label: string
  kind: AssetKind
  robotType?: RobotType
  model?: string
  status: AssetStatus
  location: string
  locationNodeId: string
  battery?: number
  task?: string
  eta?: string
}

export type TaskItem = {
  id: string
  summary: string
  stage: TaskStage
  route: string
  routeNodeIds: string[]
  owner: string
  ownerType?: RobotType
  eta: string
}

export type AlertItem = {
  id: string
  severity: AlertSeverity
  message: string
  area: string
  time: string
}

export type EventItem = {
  id: string
  time: string
  entity: string
  message: string
  tone: EventTone
}

export type TelemetryItem = {
  label: string
  value: string
  delta: string
  tone: 'ok' | 'live' | 'warn'
}

export type StatusCell = {
  label: string
  value: string
}

export type GraphNode = {
  id: string
  label: string
  col: number
  row: number
  state: 'active' | 'idle' | 'warning'
  type: 'zone' | 'path' | 'dock' | 'room'
}

export type WorkflowStage = {
  label: string
  complete: boolean
  active?: boolean
}

export type CommandLogEntry = {
  id: string
  time: string
  action: string
  status: 'queued' | 'issued' | 'completed'
  target: string
}

export type ReplayState = {
  mode: 'live' | 'replay'
  cursorLabel: string
  progressPct: number
  lastAction: string
}

export type RuntimeSnapshot = {
  assets: Asset[]
  tasks: TaskItem[]
  alerts: AlertItem[]
  events: EventItem[]
  telemetry: TelemetryItem[]
  statusCells: StatusCell[]
  graphNodes: GraphNode[]
  graphLinks: readonly [string, string][]
  workflowStages: WorkflowStage[]
  commandLog: CommandLogEntry[]
  replay: ReplayState
  runtimeMode: 'mock' | 'backend'
  runtimeLabel: string
  connectionLabel: string
}

export type ScenarioState = {
  id: string
  name: string
  status: 'idle' | 'running' | 'completed'
  message: string
  canReplay: boolean
}
