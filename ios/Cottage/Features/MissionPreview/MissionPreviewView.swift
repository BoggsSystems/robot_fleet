import SwiftUI

struct MissionPreviewView: View {
    @ObservedObject var viewModel: MissionPreviewViewModel
    let onMissionConfirmed: (MobileMission) -> Void

    var body: some View {
        let mission = viewModel.previewResponse.mission

        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Mission Preview")
                    .font(.title2.bold())
                Spacer()
                StatusBadge(status: mission.status)
            }

            Text(mission.title)
                .font(.headline)

            VStack(alignment: .leading, spacing: 8) {
                previewRow("From", mission.from ?? "Unspecified")
                previewRow("To", mission.to ?? "Unspecified")
                previewRow("Robot", mission.assignedRobotID ?? "To be assigned")
                previewRow("Summary", mission.summary)
            }

            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }

            Button("Confirm Mission") {
                Task { await viewModel.confirmMission() }
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.isConfirming)
        }
        .padding(16)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
        .onChange(of: viewModel.confirmedMission) { _, mission in
            guard let mission else { return }
            onMissionConfirmed(mission)
        }
    }

    private func previewRow(_ label: String, _ value: String) -> some View {
        HStack(alignment: .top) {
            Text(label)
                .font(.caption.weight(.semibold))
                .foregroundStyle(.secondary)
                .frame(width: 72, alignment: .leading)
            Text(value)
                .font(.subheadline)
        }
    }
}
