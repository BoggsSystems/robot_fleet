import { runtimeSnapshot } from './mockRuntime'
import type {
  AlertItem,
  Asset,
  EventItem,
  RobotType,
  RuntimeSnapshot,
  TaskItem,
  TaskStage,
  WorkflowStage,
} from './types'

type FleetRobot = {
  robot_id?: string
  name?: string
  status?: string
  fleet_status?: string
  battery?: number
  zone_id?: string
  zone?: string
  robot_type?: string
  robot_category?: string
}

type FleetTask = {
  task_id?: string
  robot_id?: string
  spec?: Record<string, unknown>
  result?: Record<string, unknown>
}

type FleetStatusResponse = {
  robots?: FleetRobot[]
  active_tasks?: FleetTask[]
  completed_tasks?: FleetTask[]
  onboarding_mode?: boolean
  registry?: {
    sites?: Array<{ site_id: string; name: string }>
    zones?: Array<{ zone_id: string; name: string; zone_type?: string }>
    tasks?: Array<{ task_id: string; task_type: string; status: string; robot_id?: string; zone_id?: string }>
    commands?: Array<{ command_id: string; command_type: string; status: string; robot_id?: string }>
  }
}

export function mergeRuntimeSnapshot(response: FleetStatusResponse | null): RuntimeSnapshot {
  if (!response) {
    return runtimeSnapshot
  }

  const base = runtimeSnapshot
  const zoneNames = new Map(
    (response.registry?.zones ?? []).map((zone) => [zone.zone_id, zone.name]),
  )

  const assets = mergeAssets(base.assets, response.robots ?? [], zoneNames)
  const tasks = mergeTasks(base.tasks, response)
  const alerts = mergeAlerts(base.alerts, response)
  const events = mergeEvents(base.events, response, tasks)
  const workflowStages = buildWorkflowStages(tasks[0]?.stage ?? base.workflowStages.find((s) => s.active)?.label)

  return {
    ...base,
    assets,
    tasks,
    alerts,
    events,
    workflowStages,
    commandLog: base.commandLog,
    replay: {
      ...base.replay,
      mode: 'live',
      cursorLabel: response.onboarding_mode ? 'Registry sync' : 'Live edge',
      progressPct: 100,
      lastAction: response.onboarding_mode ? 'Backend onboarding data merged.' : 'Backend runtime snapshot merged.',
    },
    runtimeMode: 'backend',
    runtimeLabel: response.onboarding_mode ? 'Backend / Onboarding' : 'Backend / Live',
    connectionLabel: response.onboarding_mode ? 'Registry stream' : 'WebSocket live',
    statusCells: base.statusCells.map((cell) => {
      if (cell.label === 'Connectivity') return { ...cell, value: 'Backend Linked' }
      if (cell.label === 'Runtime') return { ...cell, value: response.onboarding_mode ? 'Onboarding Mode' : 'Live Runtime' }
      if (cell.label === 'Robots Online') return { ...cell, value: `${response.robots?.length ?? 0} tracked` }
      return cell
    }),
  }
}

function mergeAssets(
  baseAssets: Asset[],
  robots: FleetRobot[],
  zoneNames: Map<string | undefined, string>,
): Asset[] {
  const mappedRobots = robots.map<Asset>((robot) => {
    const zoneLabel = zoneNames.get(robot.zone_id) ?? robot.zone ?? 'Site'
    const label = robot.name ?? robot.robot_id ?? 'Robot'
    return {
      id: robot.robot_id ?? label.toLowerCase().replace(/\s+/g, '-'),
      label,
      kind: 'robot',
      robotType: mapRobotType(robot.robot_category, robot.robot_type),
      model: robot.robot_type ?? robot.robot_category ?? 'Backend robot',
      status: mapAssetStatus(robot.fleet_status ?? robot.status),
      location: zoneLabel,
      locationNodeId: mapLocationNode(zoneLabel),
      battery: typeof robot.battery === 'number' ? robot.battery : undefined,
      task: robot.fleet_status ?? robot.status ?? 'idle',
      eta: robot.robot_type ?? 'backend',
    }
  })

  const nonRobotAssets = baseAssets.filter((asset) => asset.kind !== 'robot')
  return mappedRobots.length > 0 ? [...mappedRobots, ...nonRobotAssets] : baseAssets
}

function mergeTasks(baseTasks: TaskItem[], response: FleetStatusResponse): TaskItem[] {
  const liveTasks = [
    ...(response.active_tasks ?? []).map((task) => mapTask(task, 'in_transit')),
    ...((response.registry?.tasks ?? []).map((task) =>
      mapRegistryTask(task.task_id, task.task_type, task.status, task.robot_id, task.zone_id),
    )),
  ].filter(Boolean) as TaskItem[]

  if (liveTasks.length === 0) {
    return baseTasks
  }

  const deduped = new Map<string, TaskItem>()
  for (const task of liveTasks) deduped.set(task.id, task)
  return Array.from(deduped.values())
}

function mergeAlerts(baseAlerts: AlertItem[], response: FleetStatusResponse): AlertItem[] {
  const backendAlerts: AlertItem[] = []
  const offlineRobots = (response.robots ?? []).filter((robot) => mapAssetStatus(robot.status) === 'maintenance')
  for (const robot of offlineRobots) {
    backendAlerts.push({
      id: `alt-${robot.robot_id ?? robot.name}`,
      severity: 'warn',
      message: `${robot.name ?? robot.robot_id ?? 'Robot'} is reporting disconnected status.`,
      area: robot.zone ?? 'Site',
      time: 'LIVE',
    })
  }
  return backendAlerts.length > 0 ? [...backendAlerts, ...baseAlerts].slice(0, 5) : baseAlerts
}

function mergeEvents(baseEvents: EventItem[], response: FleetStatusResponse, tasks: TaskItem[]): EventItem[] {
  const backendEvents: EventItem[] = []
  for (const robot of response.robots ?? []) {
    backendEvents.push({
      id: `evt-robot-${robot.robot_id ?? robot.name}`,
      time: 'LIVE',
      entity: robot.name ?? robot.robot_id ?? 'Robot',
      message: `${robot.fleet_status ?? robot.status ?? 'status'} at ${robot.zone ?? 'site'}`,
      tone: robot.fleet_status === 'busy' ? 'live' : 'ok',
    })
  }

  if (tasks[0]) {
    backendEvents.unshift({
      id: `evt-task-${tasks[0].id}`,
      time: 'LIVE',
      entity: tasks[0].id,
      message: `${tasks[0].summary} is ${tasks[0].stage.replace('_', ' ')}`,
      tone: tasks[0].stage === 'completed' ? 'ok' : 'live',
    })
  }

  return backendEvents.length > 0 ? [...backendEvents, ...baseEvents].slice(0, 6) : baseEvents
}

function buildWorkflowStages(stageLabel: string | undefined): WorkflowStage[] {
  const stages = [
    { label: 'Task received', key: 'queued' },
    { label: 'Asset assigned', key: 'assigned' },
    { label: 'In transit', key: 'in_transit' },
    { label: 'Dock handoff', key: 'handoff' },
    { label: 'Interior delivery', key: 'completed' },
  ] as const

  const stageOrder: Record<string, number> = {
    queued: 0,
    assigned: 1,
    in_transit: 2,
    handoff: 3,
    completed: 4,
  }
  const current = stageOrder[stageLabel ?? 'in_transit'] ?? 2

  return stages.map((stage, index) => ({
    label: stage.label,
    complete: index < current,
    active: index === current,
  }))
}

function mapTask(task: FleetTask, stage: TaskStage): TaskItem {
  const type = typeof task.spec?.type === 'string' ? task.spec.type : undefined
  const summary = typeof task.spec?.summary === 'string' ? task.spec.summary : humanize(type ?? task.task_id ?? 'task')
  const sourceZone = typeof task.spec?.source_zone === 'string' ? task.spec.source_zone : undefined
  const destinationZone = typeof task.spec?.destination_zone === 'string' ? task.spec.destination_zone : undefined
  const route = typeof task.spec?.route === 'string'
    ? task.spec.route
    : sourceZone && destinationZone
      ? `${humanize(sourceZone)} -> ${humanize(destinationZone)}`
      : task.robot_id
        ? `Robot ${task.robot_id}`
        : 'Awaiting route'
  return {
    id: task.task_id ?? `task-${Math.random().toString(36).slice(2, 7)}`,
    summary,
    stage,
    route,
    routeNodeIds: mapRouteNodeIds(sourceZone, destinationZone),
    owner: task.robot_id ?? 'Unassigned',
    ownerType: task.robot_id ? resolveOwnerType(task.robot_id) : undefined,
    eta: stage === 'completed' ? 'Done' : 'LIVE',
  }
}

function mapRegistryTask(
  taskId: string | undefined,
  taskType: string | undefined,
  status: string | undefined,
  robotId: string | undefined,
  zoneId: string | undefined,
): TaskItem {
  const route = zoneId ? `Zone ${humanize(zoneId)}` : 'Site'
  return {
    id: taskId ?? `task-${Math.random().toString(36).slice(2, 7)}`,
    summary: humanize(taskType ?? 'task'),
    stage: mapTaskStage(status),
    route,
    routeNodeIds: mapRouteNodeIds(zoneId, zoneId),
    owner: robotId ?? 'Unassigned',
    ownerType: robotId ? resolveOwnerType(robotId) : undefined,
    eta: status === 'completed' ? 'Done' : 'Queued',
  }
}

function mapTaskStage(status: string | undefined): TaskStage {
  if (status === 'assigned') return 'assigned'
  if (status === 'running' || status === 'active') return 'in_transit'
  if (status === 'completed') return 'completed'
  return 'queued'
}

function mapAssetStatus(status: string | undefined): Asset['status'] {
  if (status === 'busy' || status === 'active') return 'active'
  if (status === 'warning' || status === 'fault' || status === 'error') return 'warning'
  if (status === 'disconnected' || status === 'offline' || status === 'maintenance') return 'maintenance'
  return 'idle'
}

function mapLocationNode(location: string): string {
  const normalized = location.toLowerCase()
  if (normalized.includes('dock')) return 'dock'
  if (normalized.includes('entry')) return 'entry'
  if (normalized.includes('kitchen')) return 'kitchen'
  if (normalized.includes('floor')) return 'main-floor'
  if (normalized.includes('path') || normalized.includes('trail') || normalized.includes('zone')) return 'trail'
  return 'landing'
}

function humanize(value: string): string {
  return value
    .replace(/[_-]+/g, ' ')
    .replace(/\b\w/g, (match) => match.toUpperCase())
}

function mapRobotType(category: string | undefined, model: string | undefined): RobotType {
  const normalized = `${category ?? ''} ${model ?? ''}`.toLowerCase()
  if (normalized.includes('quad') || normalized.includes('go2') || normalized.includes('spot')) return 'quadruped'
  if (normalized.includes('human') || normalized.includes('g1')) return 'humanoid'
  if (normalized.includes('drone') || normalized.includes('uav')) return 'drone'
  return 'unknown'
}

function resolveOwnerType(robotId: string): RobotType | undefined {
  const match = runtimeSnapshot.assets.find((asset) => asset.id === robotId || asset.label === robotId)
  return match?.robotType
}

function mapRouteNodeIds(sourceZone: string | undefined, destinationZone: string | undefined): string[] {
  const source = sourceZone ? mapLocationNode(sourceZone) : runtimeSnapshot.tasks[0].routeNodeIds[0]
  const destination = destinationZone ? mapLocationNode(destinationZone) : source
  if (source === destination) return [source]
  if ((source === 'dock' && destination === 'kitchen') || (source === 'kitchen' && destination === 'dock')) {
    return ['dock', 'entry', 'main-floor', 'kitchen']
  }
  if ((source === 'landing' && destination === 'dock') || (source === 'dock' && destination === 'landing')) {
    return ['landing', 'trail', 'dock']
  }
  return [source, destination]
}
