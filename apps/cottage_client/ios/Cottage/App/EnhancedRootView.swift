import SwiftUI

struct EnhancedRootView: View {
    let container: AppContainer
    @ObservedObject var session: AppSession
    @StateObject private var inboxViewModel = MissionInboxViewModel
    @StateObject private var robotViewModel = RobotViewModel
    @State private var workspaceState: MissionWorkspaceState = .compose
    @State private var selectedTab = 0
    
    private let tabs = ["Missions", "Robots"]
    
    init(container: AppContainer, session: AppSession) {
        self.container = container
        self.session = session
        _inboxViewModel = StateObject(
            wrappedValue: MissionInboxViewModel(missionService: container.missionService)
        )
        _robotViewModel = StateObject(
            wrappedValue: RobotViewModel(robotService: container.robotService)
        )
    }
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Missions Tab (existing functionality)
            NavigationSplitView {
                MissionInboxView(
                    viewModel: inboxViewModel,
                    onCreateMission: { workspaceState = .compose },
                    onSelectMission: { workspaceState = .detail(missionID: $0.id) },
                    onSignOut: {
                        Task { await session.signOut() }
                    }
                )
            } detail: {
                switch workspaceState {
                case .compose:
                    MissionComposerView(
                        viewModel: MissionComposerViewModel(missionService: container.missionService),
                        onPreviewReady: { preview in
                            workspaceState = preview.mission.clarificationRequired ? .clarification(preview) : .preview(preview)
                        }
                    )
                case .clarification(let preview):
                    MissionClarificationView(
                        viewModel: MissionClarificationViewModel(
                            mission: preview.mission,
                            missionService: container.missionService
                        ),
                        onPreviewResolved: { updated in
                            workspaceState = updated.mission.clarificationRequired ? .clarification(updated) : .preview(updated)
                        }
                    )
                case .preview(let preview):
                    MissionPreviewView(
                        viewModel: MissionPreviewViewModel(
                            previewResponse: preview,
                            missionService: container.missionService
                        ),
                        onMissionConfirmed: { mission in
                            workspaceState = .detail(missionID: mission.id)
                            Task { await inboxViewModel.load() }
                        }
                    )
                case .detail(let missionID):
                    MissionDetailView(
                        viewModel: MissionDetailViewModel(
                            missionID: missionID,
                            missionService: container.missionService
                        ),
                        onMissionUpdated: { mission in
                            workspaceState = .detail(missionID: mission.id)
                            Task { await inboxViewModel.load() }
                        }
                    )
                }
            }
            .tabItem {
                Label("Missions", systemImage: "list.bullet.rectangle")
            }
            .tag(0)
            
            // Robots Tab (new functionality)
            RobotManagementTabView()
                .environmentObject(robotViewModel)
            .tabItem {
                Label("Robots", systemImage: "robot")
            }
            .tag(1)
        }
        .environmentObject(inboxViewModel)
        .environmentObject(robotViewModel)
        .task {
            // Load initial data for both tabs
            await withTaskGroup(of: Void.self) { group in
                group.addTask {
                    await inboxViewModel.load()
                }
                group.addTask {
                    await robotViewModel.loadRobots()
                }
            }
        }
    }
}
