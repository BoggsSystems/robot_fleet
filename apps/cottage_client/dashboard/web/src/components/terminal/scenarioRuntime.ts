import { runtimeSnapshot } from './mockRuntime'
import type { Asset, AssetStatus, GraphNode, RuntimeSnapshot } from './types'

const SCENARIO_TASK_ID = 'tsk-grocery-transfer'

type Phase = 0 | 1 | 2 | 3 | 4

export function buildGroceriesPhase(base: RuntimeSnapshot, phase: Phase): RuntimeSnapshot {
  const taskStage = phase === 4 ? 'completed' : phase >= 2 ? 'in_transit' : phase >= 1 ? 'assigned' : 'queued'

  const scenarioTask = {
    id: SCENARIO_TASK_ID,
    summary: 'Bulk grocery transfer',
    stage: taskStage,
    route: phase >= 3 ? 'Dock -> Kitchen' : 'Landing -> Dock',
    routeNodeIds: phase >= 3 ? ['dock', 'entry', 'main-floor', 'kitchen'] : ['landing', 'trail', 'dock'],
    owner: phase === 0 ? 'Awaiting assignment' : 'Carrier 01',
    ownerType: phase === 0 ? undefined : 'quadruped',
    eta: phase === 4 ? 'Completed' : phase === 3 ? '03m 12s' : phase === 2 ? '06m 10s' : 'Queued',
  } as const

  const eventsByPhase = [
    { id: 'evt-grocery-0', time: 'LIVE', entity: 'Bulk Grocery Transfer', message: 'Scenario launched from terminal.', tone: 'live' as const },
    { id: 'evt-grocery-1', time: 'LIVE', entity: 'Service Boat', message: 'Boat arrived with high-volume grocery load.', tone: 'ok' as const },
    { id: 'evt-grocery-2', time: 'LIVE', entity: 'Carrier 01', message: 'Carrier assigned to refrigerated grocery route.', tone: 'live' as const },
    { id: 'evt-grocery-3', time: 'LIVE', entity: 'Dock Handoff', message: 'Load transferred from dock queue to interior route.', tone: 'live' as const },
    { id: 'evt-grocery-4', time: 'LIVE', entity: 'Kitchen Delivery', message: 'All grocery crates delivered to kitchen staging.', tone: 'ok' as const },
  ]

  const alerts = phase < 4
    ? [
        {
          id: 'alt-grocery',
          severity: 'warn' as const,
          message: phase < 3
            ? 'Refrigerated grocery transfer active. Complete interior handoff within 14 min.'
            : 'Cold-chain timer nominal. Final kitchen unload in progress.',
          area: phase < 3 ? 'Landing' : 'Kitchen',
          time: 'LIVE',
        },
        ...base.alerts.filter((alert) => alert.id !== 'alt-grocery'),
      ]
    : base.alerts.filter((alert) => alert.id !== 'alt-grocery')

  const assets: Asset[] = base.assets.map((asset) => {
    if (asset.id === 'carrier-01') {
      const status: AssetStatus = phase === 4 ? 'idle' : 'active'
      return {
        ...asset,
        status,
        location: phase >= 4 ? 'Kitchen' : phase >= 3 ? 'Entry' : phase >= 2 ? 'Main Dock' : 'Landing',
        locationNodeId: phase >= 4 ? 'kitchen' : phase >= 3 ? 'entry' : phase >= 2 ? 'dock' : 'landing',
        task: phase === 4 ? 'Unload complete' : 'Bulk grocery transfer',
        eta: phase === 4 ? 'Ready' : scenarioTask.eta,
      }
    }
    if (asset.id === 'service-boat-01') {
      const status: AssetStatus = phase >= 1 && phase < 3 ? 'active' : 'idle'
      return {
        ...asset,
        status,
        location: 'Main Dock',
        locationNodeId: 'dock',
        task: phase < 3 ? 'Offloading groceries' : 'Awaiting departure',
        eta: phase < 3 ? 'Docked' : 'Clear',
      }
    }
    if (asset.id === 'cargo-014') {
      const status: AssetStatus = phase === 4 ? 'idle' : 'warning'
      return {
        ...asset,
        status,
        location: phase >= 4 ? 'Kitchen' : phase >= 3 ? 'Entry' : phase >= 2 ? 'Main Dock' : 'Landing',
        locationNodeId: phase >= 4 ? 'kitchen' : phase >= 3 ? 'entry' : phase >= 2 ? 'dock' : 'landing',
        task: phase === 4 ? 'Stored' : 'Refrigerated transfer',
        eta: phase === 4 ? 'Stable' : scenarioTask.eta,
      }
    }
    return asset
  })

  const graphNodes: GraphNode[] = base.graphNodes.map((node) => {
    if (node.id === 'landing') {
      const state: GraphNode['state'] = phase < 2 ? 'active' : 'idle'
      return { ...node, state }
    }
    if (node.id === 'dock') {
      const state: GraphNode['state'] = phase >= 1 && phase < 4 ? 'active' : 'idle'
      return { ...node, state }
    }
    if (node.id === 'entry') {
      const state: GraphNode['state'] = phase === 3 ? 'active' : 'idle'
      return { ...node, state }
    }
    if (node.id === 'kitchen') {
      const state: GraphNode['state'] = phase === 4 ? 'active' : 'idle'
      return { ...node, state }
    }
    return node
  })

  return {
    ...base,
    assets,
    tasks: [scenarioTask, ...base.tasks.filter((task) => task.id !== SCENARIO_TASK_ID)].slice(0, 4),
    alerts,
    events: [eventsByPhase[phase], ...base.events.filter((event) => !event.id.startsWith('evt-grocery-'))].slice(0, 6),
    graphNodes,
    workflowStages: [
      { label: 'Task received', complete: true },
      { label: 'Boat arrived', complete: phase >= 1, active: phase === 1 },
      { label: 'Carrier assigned', complete: phase >= 2, active: phase === 2 },
      { label: 'Dock handoff', complete: phase >= 3, active: phase === 3 },
      { label: 'Kitchen delivery', complete: phase >= 4, active: phase === 4 },
    ],
  }
}

export async function tryStartBackendScenario(apiBase: string, robotId?: string) {
  const body = {
    requestText: 'Bring groceries from dock to kitchen',
    requestedBy: 'operator@local',
    context: {
      scenario: 'bulk_groceries',
      preferredRobotId: robotId ?? null,
      source: 'terminal',
    },
  }

  const dispatchMission = await fetch(`${apiBase}/api/brain/dispatch`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!dispatchMission.ok) throw new Error(`mission dispatch ${dispatchMission.status}`)

  const missionResult = await dispatchMission.json()
  if (missionResult.status === 'clarification_required') {
    throw new Error('mission clarification required')
  }

  const simulate = await fetch(`${apiBase}/api/robots/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      robotId: robotId ?? 'sim-carrier',
      scenario: 'warehouse',
    }),
  })
  if (!simulate.ok) throw new Error(`simulate ${simulate.status}`)

  return missionResult
}

export function scenarioSelectedIds(snapshot: RuntimeSnapshot) {
  const task = snapshot.tasks.find((item) => item.id === SCENARIO_TASK_ID) ?? snapshot.tasks[0]
  const asset = snapshot.assets.find((item) => item.id === 'carrier-01') ?? runtimeSnapshot.assets[0]
  const nodeId = task?.routeNodeIds?.[Math.min(task.routeNodeIds.length - 1, 1)] ?? 'landing'
  return {
    taskId: task.id,
    assetId: asset.id,
    nodeId,
  }
}
