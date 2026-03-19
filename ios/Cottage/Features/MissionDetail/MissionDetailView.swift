import SwiftUI

struct MissionDetailView: View {
    @ObservedObject var viewModel: MissionDetailViewModel
    let onMissionUpdated: (MobileMission) -> Void

    var body: some View {
        Group {
            if let mission = viewModel.mission {
                VStack(alignment: .leading, spacing: 16) {
                    HStack {
                        Text(mission.title)
                            .font(.largeTitle.bold())
                        Spacer()
                        StatusBadge(status: mission.status)
                    }

                    detailRow("From", mission.from ?? "Unspecified")
                    detailRow("To", mission.to ?? "Unspecified")
                    detailRow("Assigned Robot", mission.assignedRobotID ?? "Unassigned")
                    detailRow("Summary", mission.summary)

                    if mission.status != .completed && mission.status != .cancelled {
                        Button("Cancel Mission") {
                            Task { await viewModel.cancelMission() }
                        }
                        .buttonStyle(.bordered)
                    }

                    Spacer()
                }
                .padding(24)
            } else if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            } else {
                ProgressView()
            }
        }
        .task { await viewModel.load() }
        .onChange(of: viewModel.mission) { _, mission in
            guard let mission else { return }
            onMissionUpdated(mission)
        }
    }

    private func detailRow(_ label: String, _ value: String) -> some View {
        VStack(alignment: .leading, spacing: 4) {
            Text(label)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
            Text(value)
        }
    }
}
