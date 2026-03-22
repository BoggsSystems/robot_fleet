import SwiftUI

struct MissionInboxView: View {
    @ObservedObject var viewModel: MissionInboxViewModel
    let onCreateMission: () -> Void
    let onSelectMission: (MobileMission) -> Void
    let onSignOut: () -> Void

    var body: some View {
        Group {
            if viewModel.isLoading && viewModel.missions.isEmpty {
                VStack {
                    ProgressView()
                    Text("Loading missions...")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
            else if let errorMessage = viewModel.errorMessage, viewModel.missions.isEmpty {
                EmptyStateView(
                    title: "Mission Inbox Unavailable",
                    message: errorMessage,
                    actionTitle: "Retry",
                    action: { Task { await viewModel.load() } }
                )
            } else if viewModel.missions.isEmpty {
                EmptyStateView(
                    title: "No Missions Yet",
                    message: "Create a mission from the compose view and it will appear here for tracking.",
                    actionTitle: "New Mission",
                    action: onCreateMission
                )
            } else {
                List(viewModel.missions) { mission in
                    Button {
                        onSelectMission(mission)
                    } label: {
                        VStack(alignment: .leading, spacing: 8) {
                            HStack(alignment: .top) {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(mission.title)
                                        .font(.headline)
                                    Text(mission.requestText)
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                        .lineLimit(2)
                                }
                                Spacer()
                                StatusBadge(status: mission.status)
                            }

                            if mission.approvalRequired {
                                Text("Approval \(mission.approvalStatus.replacingOccurrences(of: "_", with: " ").capitalized)")
                                    .font(.caption.weight(.semibold))
                                    .foregroundStyle(mission.approvalStatus == "pending" ? .orange : .secondary)
                            }

                            Text(mission.summary)
                                .font(.subheadline)
                                .foregroundStyle(.secondary)

                            HStack {
                                Label(mission.from ?? "Unspecified", systemImage: "arrow.up.left.circle")
                                Spacer()
                                Label(mission.to ?? "Unspecified", systemImage: "arrow.down.right.circle")
                            }
                            .font(.caption)
                            .foregroundStyle(.secondary)
                        }
                        .padding(.vertical, 4)
                    }
                    .buttonStyle(.plain)
                }
            }
        }
        .navigationTitle("Missions")
        .toolbar {
            ToolbarItemGroup(placement: .primaryAction) {
                Button("New") {
                    onCreateMission()
                }
                Button("Sign Out") {
                    onSignOut()
                }
            }
        }
        .task { await viewModel.load() }
        .refreshable { await viewModel.load() }
    }
}
