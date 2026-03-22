import { useMemo, useState } from 'react'
import { useAuth } from './auth/AuthProvider'
import { AssetWatchPanel } from './components/terminal/AssetWatchPanel'
import { AlertsPanel } from './components/terminal/AlertsPanel'
import { CommandLogPanel } from './components/terminal/CommandLogPanel'
import { EnvironmentPanel } from './components/terminal/EnvironmentPanel'
import { EventTapePanel } from './components/terminal/EventTapePanel'
import { PropertyTwinPanel } from './components/terminal/PropertyTwinPanel'
import { QuickActionsPanel } from './components/terminal/QuickActionsPanel'
import { ReplayPanel } from './components/terminal/ReplayPanel'
import { StatusStrip } from './components/terminal/StatusStrip'
import { TaskQueuePanel } from './components/terminal/TaskQueuePanel'
import { TelemetryStrip } from './components/terminal/TelemetryStrip'
import { TopBar } from './components/terminal/TopBar'
import { TwinInspectorPanel } from './components/terminal/TwinInspectorPanel'
import { useTerminalRuntime } from './components/terminal/useTerminalRuntime'
import { WorkflowDetailPanel } from './components/terminal/WorkflowDetailPanel'
import './App.css'

function App() {
  const { user, logout } = useAuth()
  const {
    snapshot,
    scenario,
    startGroceriesScenario,
    replayScenario,
    acknowledgeAlerts,
    pauseQueue,
  } = useTerminalRuntime()
  const [selectedAssetId, setSelectedAssetId] = useState<string>('carrier-01')
  const [selectedTaskId, setSelectedTaskId] = useState<string>('tsk-001')
  const [selectedNodeId, setSelectedNodeId] = useState<string>('landing')

  const selectedAsset = useMemo(
    () => snapshot.assets.find((asset) => asset.id === selectedAssetId) ?? snapshot.assets[0],
    [selectedAssetId, snapshot.assets],
  )
  const selectedTask = useMemo(
    () => snapshot.tasks.find((task) => task.id === selectedTaskId) ?? snapshot.tasks[0],
    [selectedTaskId, snapshot.tasks],
  )
  const selectedNode = useMemo(
    () => snapshot.graphNodes.find((node) => node.id === selectedNodeId),
    [selectedNodeId, snapshot.graphNodes],
  )

  return (
    <main className="terminal">
      <TopBar
        user={user}
        onLogout={logout}
        runtimeLabel={snapshot.runtimeLabel}
        scenario={scenario}
        alertCount={snapshot.alerts.length}
      />
      <StatusStrip items={snapshot.statusCells.map((cell) => (
        cell.label === 'Connectivity'
          ? { ...cell, value: snapshot.connectionLabel }
          : cell
      ))} />

      <section className="workspace">
        <aside className="column-left">
          <AssetWatchPanel
            assets={snapshot.assets}
            selectedAssetId={selectedAssetId}
            onSelect={(assetId) => {
              setSelectedAssetId(assetId)
              const asset = snapshot.assets.find((entry) => entry.id === assetId)
              if (asset) {
                setSelectedNodeId(asset.locationNodeId)
              }
            }}
          />
          <TaskQueuePanel
            assets={snapshot.assets}
            tasks={snapshot.tasks}
            selectedTaskId={selectedTaskId}
            onSelect={(taskId) => setSelectedTaskId(taskId)}
          />
          <QuickActionsPanel
            onReplay={async () => {
              const next = await replayScenario()
              setSelectedTaskId(next.taskId)
              setSelectedAssetId(next.assetId)
              setSelectedNodeId(next.nodeId)
            }}
            onStartScenario={async () => {
              const next = await startGroceriesScenario()
              setSelectedTaskId(next.taskId)
              setSelectedAssetId(next.assetId)
              setSelectedNodeId(next.nodeId)
            }}
            onAcknowledge={acknowledgeAlerts}
            onPause={pauseQueue}
          />
        </aside>

        <section className="column-center">
          <PropertyTwinPanel
            assets={snapshot.assets}
            nodes={snapshot.graphNodes}
            links={snapshot.graphLinks}
            selectedNodeId={selectedNodeId}
            selectedTask={selectedTask}
            onSelectNode={setSelectedNodeId}
          />

          <div className="center-lower-grid">
            <WorkflowDetailPanel assets={snapshot.assets} task={selectedTask} stages={snapshot.workflowStages} scenario={scenario} />
            <TwinInspectorPanel asset={selectedAsset} node={selectedNode} task={selectedTask} />
          </div>
        </section>

        <aside className="column-right">
          <EventTapePanel events={snapshot.events} />
          <AlertsPanel alerts={snapshot.alerts} />
          <ReplayPanel replay={snapshot.replay} scenario={scenario} />
          <EnvironmentPanel />
        </aside>
      </section>

      <section className="deep-console">
        <CommandLogPanel items={snapshot.commandLog} />
      </section>

      <TelemetryStrip items={snapshot.telemetry} />
    </main>
  )
}

export default App
