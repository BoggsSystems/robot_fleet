import { useEffect, useMemo, useState } from 'react'
import { runtimeSnapshot } from './mockRuntime'
import { mergeRuntimeSnapshot } from './runtimeAdapter'
import { buildGroceriesPhase, scenarioSelectedIds, tryStartBackendScenario } from './scenarioRuntime'
import type { CommandLogEntry, ReplayState, RuntimeSnapshot, ScenarioState, TaskItem } from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''
const WS_BASE = import.meta.env.VITE_WS_URL ?? ''

type RuntimeMode = 'mock' | 'backend'

type RuntimeState = {
  snapshot: RuntimeSnapshot
  mode: RuntimeMode
  isConnected: boolean
  scenario: ScenarioState
  startGroceriesScenario: () => Promise<{ taskId: string; assetId: string; nodeId: string }>
  replayScenario: () => Promise<{ taskId: string; assetId: string; nodeId: string }>
  acknowledgeAlerts: () => void
  pauseQueue: () => void
  pauseMission: (task?: TaskItem) => Promise<void>
  resumeMission: (task?: TaskItem) => Promise<void>
  retryMission: (task?: TaskItem) => Promise<void>
  previewReplan: (task?: TaskItem) => Promise<void>
  applyReplan: (task?: TaskItem) => Promise<void>
  failTask: (task?: TaskItem) => Promise<void>
  approveProposal: (missionId: string) => Promise<void>
  dispatchProposal: (missionId: string) => Promise<void>
}

export function useTerminalRuntime(): RuntimeState {
  const [baseSnapshot, setBaseSnapshot] = useState<RuntimeSnapshot>(runtimeSnapshot)
  const [mode, setMode] = useState<RuntimeMode>('mock')
  const [isConnected, setIsConnected] = useState(false)
  const [scenarioPhase, setScenarioPhase] = useState<number | null>(null)
  const [commandLog, setCommandLog] = useState<CommandLogEntry[]>(runtimeSnapshot.commandLog)
  const [replay, setReplay] = useState<ReplayState>(runtimeSnapshot.replay)
  const [scenario, setScenario] = useState<ScenarioState>({
    id: 'bulk-groceries',
    name: 'Bulk Grocery Transfer',
    status: 'idle',
    message: 'Ready to stage a dock-to-kitchen grocery run.',
    canReplay: false,
  })

  useEffect(() => {
    let cancelled = false
    let socket: WebSocket | null = null

    async function primeRuntime() {
      try {
        const response = await fetch(`${API_BASE}/api/fleet/status`)
        if (!response.ok) throw new Error(`HTTP ${response.status}`)
        const data = await response.json()
        if (cancelled) return
        setBaseSnapshot(mergeRuntimeSnapshot(data))
        setMode('backend')
      } catch {
        if (!cancelled) {
          setBaseSnapshot(runtimeSnapshot)
          setMode('mock')
        }
      }
    }

    function connectSocket() {
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
      const defaultWs = `${protocol}//${window.location.host}/ws`
      const url = WS_BASE || defaultWs

      try {
        socket = new WebSocket(url)
      } catch {
        return
      }

      socket.onopen = () => {
        if (cancelled) return
        setIsConnected(true)
        setMode('backend')
      }

      socket.onmessage = (event) => {
        if (cancelled) return
        try {
          const data = JSON.parse(event.data)
          setBaseSnapshot(mergeRuntimeSnapshot(data))
          setMode('backend')
        } catch {
          setBaseSnapshot(runtimeSnapshot)
          setMode('mock')
        }
      }

      socket.onerror = () => {
        if (cancelled) return
        setIsConnected(false)
        setBaseSnapshot(runtimeSnapshot)
        setMode('mock')
      }

      socket.onclose = () => {
        if (cancelled) return
        setIsConnected(false)
      }
    }

    void primeRuntime()
    connectSocket()

    return () => {
      cancelled = true
      socket?.close()
    }
  }, [])

  useEffect(() => {
    if (scenarioPhase === null) return
    if (scenarioPhase >= 4) {
      setScenario((current) => ({
        ...current,
        status: 'completed',
        message: 'Groceries delivered to the kitchen staging area.',
        canReplay: true,
      }))
      setReplay({
        mode: 'replay',
        cursorLabel: 'Scenario complete',
        progressPct: 100,
        lastAction: 'Bulk grocery transfer completed at kitchen staging.',
      })
      setCommandLog((current) => [
        scenarioCommand('completed', 'Finalize kitchen unload', 'Kitchen staging'),
        ...current,
      ].slice(0, 8))
      return
    }

    const timer = window.setTimeout(() => {
      const nextPhase = Math.min((scenarioPhase ?? 0) + 1, 4)
      setScenarioPhase((current) => (current === null ? null : nextPhase))
      setScenario((current) => ({
        ...current,
        status: 'running',
        message: scenarioMessage(nextPhase),
        canReplay: false,
      }))
      setReplay({
        mode: 'replay',
        cursorLabel: `Phase ${nextPhase} / 4`,
        progressPct: Math.round((nextPhase / 4) * 100),
        lastAction: scenarioMessage(nextPhase),
      })
      setCommandLog((current) => [
        scenarioCommand(
          nextPhase >= 4 ? 'completed' : 'issued',
          scenarioCommandLabel(nextPhase),
          scenarioCommandTarget(nextPhase),
        ),
        ...current,
      ].slice(0, 8))
    }, 1800)

    return () => window.clearTimeout(timer)
  }, [scenarioPhase])

  const snapshot = useMemo(() => {
    const merged = scenarioPhase === null ? baseSnapshot : buildGroceriesPhase(baseSnapshot, scenarioPhase as 0 | 1 | 2 | 3 | 4)
    return {
      ...merged,
      commandLog,
      replay,
      runtimeMode: mode,
      runtimeLabel: mode === 'backend' ? merged.runtimeLabel : 'Mock Runtime',
      connectionLabel: mode === 'backend' ? (isConnected ? 'WebSocket live' : 'HTTP snapshot') : 'Standalone mock',
    }
  }, [baseSnapshot, scenarioPhase, mode, isConnected, commandLog, replay])

  async function startScenario() {
    setScenario({
      id: 'bulk-groceries',
      name: 'Bulk Grocery Transfer',
      status: 'running',
      message: scenarioMessage(0),
      canReplay: false,
    })
    setScenarioPhase(0)
    setReplay({
      mode: 'replay',
      cursorLabel: 'Phase 0 / 4',
      progressPct: 0,
      lastAction: 'Scenario launched from terminal.',
    })
    setCommandLog((current) => [
      scenarioCommand('queued', 'Launch bulk grocery transfer', 'Dock corridor'),
      ...current,
    ].slice(0, 8))

    if (mode === 'backend') {
      try {
        const robotId = snapshot.assets.find((item) => item.kind === 'robot')?.id
        await tryStartBackendScenario(API_BASE, robotId)
      } catch {
        // Keep the scenario running locally even if backend actions fail.
      }
    }

    return scenarioSelectedIds(buildGroceriesPhase(baseSnapshot, 0))
  }

  function acknowledgeAlerts() {
    setScenario((current) => ({
      ...current,
      message: 'Operator acknowledged active grocery transfer alerts.',
    }))
    setCommandLog((current) => [
      scenarioCommand('completed', 'Acknowledge active alerts', 'Operations terminal'),
      ...current,
    ].slice(0, 8))
  }

  function pauseQueue() {
    setScenario((current) => ({
      ...current,
      message: 'Queue pause requested. Scenario remains in local replay mode.',
    }))
    setCommandLog((current) => [
      scenarioCommand('issued', 'Request queue pause', 'Task queue'),
      ...current,
    ].slice(0, 8))
  }

  async function refreshRuntimeSnapshot() {
    try {
      const response = await fetch(`${API_BASE}/api/fleet/status`)
      if (!response.ok) throw new Error(`HTTP ${response.status}`)
      const data = await response.json()
      setBaseSnapshot(mergeRuntimeSnapshot(data))
      setMode('backend')
    } catch {
      // Leave the current snapshot in place if refresh fails.
    }
  }

  async function missionControl(path: string, action: string, target: string, status: CommandLogEntry['status']) {
    if (mode !== 'backend') return
    const response = await fetch(`${API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ requestedBy: 'operator@local' }),
    })
    if (!response.ok) {
      throw new Error(`Mission control failed with HTTP ${response.status}`)
    }
    setCommandLog((current) => [
      scenarioCommand(status, action, target),
      ...current,
    ].slice(0, 8))
    await refreshRuntimeSnapshot()
  }

  async function pauseMission(task?: TaskItem) {
    if (!task?.missionId) return
    await missionControl(`/api/mobile/missions/${task.missionId}/pause`, 'Pause mission', task.summary, 'issued')
    setScenario((current) => ({
      ...current,
      status: 'paused',
      message: `Mission paused at ${task.summary}.`,
    }))
  }

  async function resumeMission(task?: TaskItem) {
    if (!task?.missionId) return
    await missionControl(`/api/mobile/missions/${task.missionId}/resume`, 'Resume mission', task.summary, 'completed')
    setScenario((current) => ({
      ...current,
      status: 'running',
      message: `Mission resumed from ${task.summary}.`,
    }))
  }

  async function retryMission(task?: TaskItem) {
    if (!task?.missionId) return
    await missionControl(`/api/mobile/missions/${task.missionId}/retry`, 'Retry mission', task.summary, 'issued')
    setScenario((current) => ({
      ...current,
      status: 'running',
      message: `Retry requested for ${task.summary}.`,
    }))
  }

  async function failTask(task?: TaskItem) {
    if (mode !== 'backend' || !task?.id) return
    const response = await fetch(`${API_BASE}/api/backend/tasks/${task.id}/status`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        status: 'failed',
        result: { reason: 'Operator-marked failure from terminal' },
      }),
    })
    if (!response.ok) {
      throw new Error(`Task failure update failed with HTTP ${response.status}`)
    }
    setCommandLog((current) => [
      scenarioCommand('issued', 'Mark task failed', task.summary),
      ...current,
    ].slice(0, 8))
    setScenario((current) => ({
      ...current,
      status: 'blocked',
      message: `${task.summary} marked failed. Awaiting retry or operator intervention.`,
    }))
    await refreshRuntimeSnapshot()
  }

  async function previewReplan(task?: TaskItem) {
    if (!task?.missionId) return
    await missionControl(`/api/mobile/missions/${task.missionId}/replan-preview`, 'Preview mission replan', task.summary, 'issued')
  }

  async function applyReplan(task?: TaskItem) {
    if (!task?.missionId) return
    await missionControl(`/api/mobile/missions/${task.missionId}/replan-apply`, 'Apply mission replan', task.summary, 'issued')
  }

  async function approveProposal(missionId: string) {
    if (mode !== 'backend') return
    const response = await fetch(`${API_BASE}/api/mobile/missions/${missionId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approvedBy: 'operator@local' }),
    })
    if (!response.ok) {
      throw new Error(`Mission approval failed with HTTP ${response.status}`)
    }
    setCommandLog((current) => [
      scenarioCommand('completed', 'Approve mission', missionId),
      ...current,
    ].slice(0, 8))
    await refreshRuntimeSnapshot()
  }

  async function dispatchProposal(missionId: string) {
    if (mode !== 'backend') return
    const response = await fetch(`${API_BASE}/api/mobile/missions/${missionId}/dispatch`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ confirmedBy: 'operator@local' }),
    })
    if (!response.ok) {
      throw new Error(`Mission dispatch failed with HTTP ${response.status}`)
    }
    setCommandLog((current) => [
      scenarioCommand('completed', 'Dispatch approved mission', missionId),
      ...current,
    ].slice(0, 8))
    await refreshRuntimeSnapshot()
  }

  return useMemo(() => ({
    snapshot,
    mode,
    isConnected,
    scenario,
    startGroceriesScenario: startScenario,
    replayScenario: startScenario,
    acknowledgeAlerts,
    pauseQueue,
    pauseMission,
    resumeMission,
    retryMission,
    previewReplan,
    applyReplan,
    failTask,
    approveProposal,
    dispatchProposal,
  }), [snapshot, mode, isConnected, scenario])
}

function scenarioCommand(
  status: CommandLogEntry['status'],
  action: string,
  target: string,
): CommandLogEntry {
  return {
    id: `cmd-${Math.random().toString(36).slice(2, 8)}`,
    time: 'LIVE',
    action,
    status,
    target,
  }
}

function scenarioCommandLabel(phase: number) {
  switch (phase) {
    case 1:
      return 'Confirm grocery boat arrival'
    case 2:
      return 'Assign carrier to refrigerated route'
    case 3:
      return 'Advance dock handoff to interior route'
    case 4:
      return 'Close cold-chain transfer'
    default:
      return 'Monitor active scenario'
  }
}

function scenarioCommandTarget(phase: number) {
  switch (phase) {
    case 1:
      return 'Service Boat'
    case 2:
      return 'Carrier 01'
    case 3:
      return 'Dock handoff'
    case 4:
      return 'Kitchen staging'
    default:
      return 'Cottage terminal'
  }
}

function scenarioMessage(phase: number) {
  switch (phase) {
    case 0:
      return 'Boat and landing teams are staging a bulk grocery load.'
    case 1:
      return 'Boat is docked and the grocery pallets are staged for carrier pickup.'
    case 2:
      return 'Carrier 01 is moving the grocery load from dock to entry.'
    case 3:
      return 'Dock handoff complete. Interior delivery route is now active.'
    case 4:
      return 'Groceries delivered to the kitchen staging area.'
    default:
      return 'Scenario ready.'
  }
}
