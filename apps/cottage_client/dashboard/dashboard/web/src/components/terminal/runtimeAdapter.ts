import { runtimeSnapshot } from './mockRuntime'
import type {
  AlertItem,
  Asset,
  EventItem,
  MissionProposalItem,
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

type FleetRegistryTask = {
  task_id: string
  task_type: string
  status: string
  robot_id?: string
  zone_id?: string
  spec?: Record<string, unknown>
  result?: Record<string, unknown>
}

type FleetMission = {
  mission_id: string
  request_text: string
  status: string
  task_ids?: string[]
  request?: {
    context?: Record<string, unknown>
  }
  proposal?: {
    plan?: {
      summary?: string
      operator_notes?: string[]
      candidate_steps?: Array<{
        task_id: string
        summary: string
        route_labels?: string[]
        candidate_allocations?: Array<{
          display_name?: string
        }>
      }>
    }
    assumptions?: string[]
    warnings?: string[]
  }
  validated_plan?: {
    executable?: boolean
    blockingReasons?: string[]
    blocking_reasons?: string[]
    warnings?: string[]
  }
  approval?: {
    status?: string
    required?: boolean
  }
  metadata?: {
    mission_events?: Array<{
      id: string
      time: string
      message: string
      tone?: 'live' | 'ok' | 'warn'
      task_id?: string
      status?: string
    }>
    pending_replan?: {
      summary?: string
      reviewSummary?: string
      provider?: string
      operatorNotes?: string[]
      routeLabels?: string[]
    }
  }
}

type FleetStatusResponse = {
  robots?: FleetRobot[]
  active_tasks?: FleetTask[]
  completed_tasks?: FleetTask[]
  onboarding_mode?: boolean
  registry?: {
    sites?: Array<{ site_id: string; name: string }>
    zones?: Array<{ zone_id: string; name: string; zone_type?: string }>
    tasks?: FleetRegistryTask[]
    commands?: Array<{ command_id: string; command_type: string; status: string; robot_id?: string }>
    missions?: FleetMission[]
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
  const proposals = mergeProposals(response)
  const alerts = mergeAlerts(base.alerts, response)
  const events = mergeEvents(base.events, response, tasks)
  const workflowStages = buildWorkflowStages(tasks, tasks[0]?.id)

  return {
    ...base,
    assets,
    tasks,
    proposals,
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
  const missionStatusById = new Map<string, FleetMission>(
    (response.registry?.missions ?? []).map((mission) => [mission.mission_id, mission]),
  )
  const liveTasks = [
    ...(response.active_tasks ?? []).map((task) => mapTask(task, 'in_transit')),
    ...((response.registry?.tasks ?? []).map((task) =>
      mapRegistryTask(task, missionStatusById),
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
  const missionEvents = (response.registry?.missions ?? [])
    .flatMap((mission) =>
      (mission.metadata?.mission_events ?? []).map((event) => ({
        rawTime: event.time,
        item: {
          id: event.id,
          time: event.time === 'LIVE' ? event.time : timeLabel(event.time),
          entity: mission.request_text,
          message: event.message,
          tone: event.tone ?? 'live',
        } satisfies EventItem,
      })),
    )
    .sort((left, right) => right.rawTime.localeCompare(left.rawTime))
    .map((entry) => entry.item)

  if (missionEvents.length > 0) {
    backendEvents.push(...missionEvents.slice(0, 4))
  }
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

function buildWorkflowStages(tasks: TaskItem[], selectedTaskId: string | undefined): WorkflowStage[] {
  const selectedTask = tasks.find((task) => task.id === selectedTaskId) ?? tasks[0]
  if (!selectedTask?.missionId) {
    const stageOrder: Record<string, number> = {
      queued: 0,
      assigned: 1,
      in_transit: 2,
      completed: 3,
    }
    const labels = ['Task received', 'Asset assigned', 'In transit', 'Completed']
    const current = stageOrder[selectedTask?.stage ?? 'in_transit'] ?? 2
    return labels.map((label, index) => ({
      label,
      complete: index < current,
      active: index === current,
    }))
  }

  const missionTasks = tasks
    .filter((task) => task.missionId === selectedTask.missionId)
    .sort((a, b) => (a.stepIndex ?? 999) - (b.stepIndex ?? 999))

  return missionTasks.map((task, index) => ({
    label: task.summary,
    complete: task.stage === 'completed',
    active:
      task.id === selectedTask.id ||
      (selectedTask.stage === 'completed' && index === missionTasks.length - 1) ||
      (!missionTasks.some((candidate) => candidate.stage === 'assigned' || candidate.stage === 'in_transit') &&
        task.stage !== 'completed' &&
        task.id === missionTasks.find((candidate) => candidate.stage !== 'completed')?.id),
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

function mergeProposals(response: FleetStatusResponse): MissionProposalItem[] {
  return (response.registry?.missions ?? [])
    .filter((mission) => {
      const approvalStatus = mission.approval?.status ?? 'not_required'
      const hasLiveTasks = Array.isArray(mission.task_ids) && mission.task_ids.length > 0
      return !hasLiveTasks && (approvalStatus === 'pending' || approvalStatus === 'approved')
    })
    .map((mission) => ({
      id: mission.mission_id,
      title: humanize(mission.request_text),
      status: mission.status,
      approvalStatus: mission.approval?.status ?? 'pending',
      executable: mission.validated_plan?.executable,
      warnings: mission.proposal?.warnings ?? [],
      assumptions: mission.proposal?.assumptions ?? [],
      operatorNotes: mission.proposal?.plan?.operator_notes ?? [],
      blockingReasons: mission.validated_plan?.blocking_reasons ?? mission.validated_plan?.blockingReasons ?? [],
      summary: mission.proposal?.plan?.summary,
      replanSummary: mission.metadata?.pending_replan?.summary,
      steps: (mission.proposal?.plan?.candidate_steps ?? []).map((step) => ({
        id: step.task_id,
        summary: step.summary,
        topCandidate: step.candidate_allocations?.[0]?.display_name,
        routeLabels: step.route_labels ?? [],
      })),
    }))
}

function mapRegistryTask(task: FleetRegistryTask, missionStatusById: Map<string, FleetMission>): TaskItem {
  const spec = task.spec ?? {}
  const context = asRecord(spec.context)
  const sourceZone = typeof spec.source_zone === 'string' ? spec.source_zone : task.zone_id
  const destinationZone = typeof spec.destination_zone === 'string' ? spec.destination_zone : sourceZone
  const route = typeof spec.route === 'string'
    ? spec.route
    : sourceZone && destinationZone
      ? `${humanize(sourceZone)} -> ${humanize(destinationZone)}`
      : sourceZone
        ? `Zone ${humanize(sourceZone)}`
        : 'Site'
  const owner = task.robot_id ?? asOptionalString(spec.planned_robot_id) ?? 'Unassigned'
  const totalSteps = asOptionalNumber(spec.total_steps)
  const missionId = asOptionalString(spec.mission_id)
  const mission = missionId ? missionStatusById.get(missionId) : undefined
  return {
    id: task.task_id ?? `task-${Math.random().toString(36).slice(2, 7)}`,
    summary: asOptionalString(spec.summary) ?? humanize(task.task_type ?? 'task'),
    stage: mapTaskStage(task.status),
    route,
    routeNodeIds: mapRouteNodeIds(sourceZone, destinationZone),
    owner,
    ownerType: owner !== 'Unassigned' ? resolveOwnerType(owner) : undefined,
    eta: task.status === 'completed' ? 'Done' : task.status === 'assigned' ? 'Ready' : 'Queued',
    missionId,
    missionStatus: mission?.status,
    stepIndex: asOptionalNumber(spec.step_index),
    totalSteps,
    dependsOn: asStringArray(spec.depends_on),
    fallbackRobotIds: asStringArray(spec.fallback_robot_ids),
    assignmentRationale: asOptionalString(spec.assignment_rationale),
    blockedReason: asOptionalString((task.result ?? {}).reason) ?? asOptionalString(context?.failure_reason),
    approvalRequired: mission?.approval?.required,
    approvalStatus: mission?.approval?.status,
    proposalWarnings: mission?.proposal?.warnings ?? [],
    validatedWarnings: mission?.validated_plan?.warnings ?? [],
    replanAvailable: Boolean(mission?.metadata?.pending_replan),
    replanSummary: mission?.metadata?.pending_replan?.reviewSummary ?? mission?.metadata?.pending_replan?.summary,
  }
}

function mapTaskStage(status: string | undefined): TaskStage {
  if (status === 'assigned') return 'assigned'
  if (status === 'running' || status === 'active') return 'in_transit'
  if (status === 'completed') return 'completed'
  return 'queued'
}

function asOptionalString(value: unknown): string | undefined {
  return typeof value === 'string' && value.length > 0 ? value : undefined
}

function asOptionalNumber(value: unknown): number | undefined {
  return typeof value === 'number' ? value : undefined
}

function asStringArray(value: unknown): string[] | undefined {
  if (!Array.isArray(value)) return undefined
  return value.filter((item): item is string => typeof item === 'string')
}

function asRecord(value: unknown): Record<string, unknown> | undefined {
  return value && typeof value === 'object' && !Array.isArray(value)
    ? value as Record<string, unknown>
    : undefined
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

function timeLabel(value: string): string {
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return 'LIVE'
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false })
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
