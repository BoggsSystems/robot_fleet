import { useMemo, useState } from 'react'
import { useAuth } from './auth/AuthProvider'
import { AssetWatchPanel } from './components/terminal/AssetWatchPanel'
import { AlertsPanel } from './components/terminal/AlertsPanel'
import { CommandLogPanel } from './components/terminal/CommandLogPanel'
import { EnvironmentPanel } from './components/terminal/EnvironmentPanel'
import { EventTapePanel } from './components/terminal/EventTapePanel'
import { PropertyTwinPanel } from './components/terminal/PropertyTwinPanel'
import { ProposalReviewPanel } from './components/terminal/ProposalReviewPanel'
import { QuickActionsPanel } from './components/terminal/QuickActionsPanel'
import { ReplayPanel } from './components/terminal/ReplayPanel'
import { StatusStrip } from './components/terminal/StatusStrip'
import { TaskQueuePanel } from './components/terminal/TaskQueuePanel'
import { TelemetryStrip } from './components/terminal/TelemetryStrip'
import { TopBar } from './components/terminal/TopBar'
import { TwinInspectorPanel } from './components/terminal/TwinInspectorPanel'
import { useTerminalRuntime } from './components/terminal/useTerminalRuntime'
import { WorkflowDetailPanel } from './components/terminal/WorkflowDetailPanel'
import { CustomerOnboardingAdmin } from './components/CustomerOnboardingAdmin'
import type { TaskItem, WorkflowStage } from './components/terminal/types'
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
    pauseMission,
    resumeMission,
    retryMission,
    previewReplan,
    applyReplan,
    failTask,
    approveProposal,
    dispatchProposal,
  } = useTerminalRuntime()
  const [selectedAssetId, setSelectedAssetId] = useState<string>('carrier-01')
  const [selectedTaskId, setSelectedTaskId] = useState<string>('tsk-001')
  const [selectedNodeId, setSelectedNodeId] = useState<string>('landing')
  const [selectedProposalId, setSelectedProposalId] = useState<string>('msn-prop-001')
  const [currentView, setCurrentView] = useState<'terminal' | 'customer-onboarding'>('terminal')

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
  const selectedWorkflowStages = useMemo(
    () => buildSelectedWorkflowStages(snapshot.tasks, selectedTask),
    [snapshot.tasks, selectedTask],
  )

  return (
    <main className="terminal">
      <TopBar
        user={user}
        onLogout={logout}
        runtimeLabel={snapshot.runtimeLabel}
        scenario={scenario}
        alertCount={snapshot.alerts.length}
        onSwitchView={() => setCurrentView(currentView === 'terminal' ? 'customer-onboarding' : 'terminal')}
        currentView={currentView}
      />
      
      {currentView === 'terminal' ? (
        <>
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
            selectedTask={selectedTask}
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
            onPauseMission={() => void pauseMission(selectedTask)}
            onResumeMission={() => void resumeMission(selectedTask)}
            onRetryMission={() => void retryMission(selectedTask)}
            onPreviewReplan={() => void previewReplan(selectedTask)}
            onApplyReplan={() => void applyReplan(selectedTask)}
            onFailTask={() => void failTask(selectedTask)}
          />
        </aside>

        <section className="column-center">
          <ProposalReviewPanel
            proposals={snapshot.proposals}
            selectedProposalId={selectedProposalId}
            onSelect={setSelectedProposalId}
            onApprove={(missionId) => void approveProposal(missionId)}
            onDispatch={(missionId) => void dispatchProposal(missionId)}
          />
          <PropertyTwinPanel
            assets={snapshot.assets}
            nodes={snapshot.graphNodes}
            links={snapshot.graphLinks}
            selectedNodeId={selectedNodeId}
            selectedTask={selectedTask}
            onSelectNode={setSelectedNodeId}
          />

          <div className="center-lower-grid">
            <WorkflowDetailPanel assets={snapshot.assets} task={selectedTask} stages={selectedWorkflowStages} scenario={scenario} />
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
        </>
        ) : (
          <CustomerOnboardingAdmin 
            onSelectCustomer={(customer) => {
              console.log('Selected customer:', customer);
            }}
            onCancel={() => setCurrentView('terminal')}
          />
        )}
    </main>
  )
}

export default App

function buildSelectedWorkflowStages(tasks: TaskItem[], selectedTask: TaskItem | undefined): WorkflowStage[] {
  if (!selectedTask?.missionId) {
    return [
      { label: 'Task received', complete: selectedTask?.stage !== 'queued', active: selectedTask?.stage === 'queued' },
      { label: 'Asset assigned', complete: selectedTask?.stage === 'in_transit' || selectedTask?.stage === 'completed', active: selectedTask?.stage === 'assigned' },
      { label: 'In transit', complete: selectedTask?.stage === 'completed', active: selectedTask?.stage === 'in_transit' },
      { label: 'Completed', complete: selectedTask?.stage === 'completed', active: selectedTask?.stage === 'completed' },
    ]
  }

  const missionTasks = tasks
    .filter((task) => task.missionId === selectedTask.missionId)
    .sort((a, b) => (a.stepIndex ?? 999) - (b.stepIndex ?? 999))

  return missionTasks.map((task) => ({
    label: task.summary,
    complete: task.stage === 'completed',
    active:
      task.id === selectedTask.id ||
      ((selectedTask.stage === 'completed' || selectedTask.stage === 'assigned' || selectedTask.stage === 'in_transit') &&
        task.id === missionTasks.find((candidate) => candidate.stage === 'assigned' || candidate.stage === 'in_transit')?.id) ||
      (task.stage === 'queued' && task.id === missionTasks.find((candidate) => candidate.stage === 'queued')?.id),
  }))
}
