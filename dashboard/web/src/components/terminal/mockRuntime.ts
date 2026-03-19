import type { RuntimeSnapshot } from './types'

export const runtimeSnapshot: RuntimeSnapshot = {
  assets: [
    { id: 'carrier-01', label: 'Carrier 01', kind: 'robot', robotType: 'quadruped', model: 'Unitree Go2', status: 'active', location: 'Landing', locationNodeId: 'landing', battery: 86, task: 'Dock handoff', eta: '02m 14s' },
    { id: 'carrier-02', label: 'Carrier 02', kind: 'robot', robotType: 'humanoid', model: 'Unitree G1', status: 'idle', location: 'Entry', locationNodeId: 'entry', battery: 94, task: 'Standby', eta: 'Ready' },
    { id: 'service-boat-01', label: 'Service Boat', kind: 'boat', robotType: 'boat', model: 'Shore Tender', status: 'active', location: 'Main Dock', locationNodeId: 'dock', task: 'Inbound supplies', eta: '00m 52s' },
    { id: 'cargo-014', label: 'Cargo 014', kind: 'cargo', robotType: 'cargo', model: 'Cold Storage Bin', status: 'warning', location: 'Landing', locationNodeId: 'landing', task: 'Cold storage', eta: '11m 48s' },
  ],
  tasks: [
    { id: 'tsk-001', summary: 'Landing to dock delivery', stage: 'in_transit', route: 'Landing -> Dock', routeNodeIds: ['landing', 'trail', 'dock'], owner: 'Carrier 01', ownerType: 'quadruped', eta: '02m 14s' },
    { id: 'tsk-002', summary: 'Dock to kitchen handoff', stage: 'queued', route: 'Dock -> Kitchen', routeNodeIds: ['dock', 'entry', 'main-floor', 'kitchen'], owner: 'Unassigned', eta: 'Pending' },
    { id: 'tsk-003', summary: 'Perimeter inspection', stage: 'assigned', route: 'Entry -> Trail', routeNodeIds: ['entry', 'trail'], owner: 'Carrier 02', ownerType: 'humanoid', eta: '06m 40s' },
  ],
  alerts: [
    { id: 'alt-001', severity: 'warn', message: 'Cargo 014 requires temperature-controlled transfer within 12 min.', area: 'Landing', time: '10:14:22' },
    { id: 'alt-002', severity: 'info', message: 'Boat arrival synchronized with dock window.', area: 'Main Dock', time: '10:11:03' },
    { id: 'alt-003', severity: 'fault', message: 'West path sensor heartbeat is stale. Twin fallback interpolation enabled.', area: 'Path', time: '10:06:17' },
  ],
  events: [
    { id: 'evt-001', time: '10:14:22', entity: 'Cargo 014', message: 'Temperature threshold window opened.', tone: 'warn' },
    { id: 'evt-002', time: '10:13:01', entity: 'Carrier 01', message: 'Route locked to dock corridor.', tone: 'live' },
    { id: 'evt-003', time: '10:11:03', entity: 'Service Boat', message: 'Approach confirmed at Main Dock.', tone: 'ok' },
    { id: 'evt-004', time: '10:08:42', entity: 'Twin Runtime', message: 'Placeholder graph provisioned for Cottage.', tone: 'ok' },
    { id: 'evt-005', time: '10:06:17', entity: 'Path Sensor', message: 'Heartbeat stale, switching to estimated occupancy.', tone: 'warn' },
  ],
  telemetry: [
    { label: 'Robot Battery Avg', value: '90.0%', delta: '+1.2%', tone: 'ok' },
    { label: 'Task Throughput', value: '3 / hr', delta: 'LIVE', tone: 'live' },
    { label: 'Dock Cycle Time', value: '6m 12s', delta: '-38s', tone: 'ok' },
    { label: 'Alert Load', value: '3 open', delta: 'WATCH', tone: 'warn' },
  ],
  statusCells: [
    { label: 'Connectivity', value: 'Edge Linked' },
    { label: 'Dock Window', value: 'Open' },
    { label: 'Robots Online', value: '2 / 2' },
    { label: 'Boat Status', value: 'Approaching' },
    { label: 'Runtime', value: 'Placeholder Graph' },
  ],
  graphNodes: [
    { id: 'landing', label: 'Landing', col: 1, row: 1, state: 'active', type: 'zone' },
    { id: 'trail', label: 'Path', col: 2, row: 1, state: 'warning', type: 'path' },
    { id: 'dock', label: 'Main Dock', col: 3, row: 1, state: 'active', type: 'dock' },
    { id: 'entry', label: 'Entry', col: 2, row: 2, state: 'idle', type: 'room' },
    { id: 'main-floor', label: 'Main Floor', col: 3, row: 2, state: 'idle', type: 'room' },
    { id: 'kitchen', label: 'Kitchen', col: 4, row: 2, state: 'idle', type: 'room' },
  ],
  graphLinks: [
    ['landing', 'trail'],
    ['trail', 'dock'],
    ['trail', 'entry'],
    ['entry', 'main-floor'],
    ['main-floor', 'kitchen'],
  ],
  workflowStages: [
    { label: 'Task received', complete: true },
    { label: 'Asset assigned', complete: true },
    { label: 'In transit', complete: true, active: true },
    { label: 'Dock handoff', complete: false },
    { label: 'Interior delivery', complete: false },
  ],
  commandLog: [
    { id: 'cmd-001', time: '10:14:22', action: 'Issue refrigerated transfer watch', status: 'completed', target: 'Cargo 014' },
    { id: 'cmd-002', time: '10:13:01', action: 'Lock dock corridor route', status: 'issued', target: 'Carrier 01' },
    { id: 'cmd-003', time: '10:11:03', action: 'Confirm dock arrival window', status: 'completed', target: 'Service Boat' },
  ],
  replay: {
    mode: 'live',
    cursorLabel: 'Live edge',
    progressPct: 100,
    lastAction: 'Twin runtime tracking active grocery staging.',
  },
  runtimeMode: 'mock',
  runtimeLabel: 'Mock Runtime',
  connectionLabel: 'Standalone mock',
}
