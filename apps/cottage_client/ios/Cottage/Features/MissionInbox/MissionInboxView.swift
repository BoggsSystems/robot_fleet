import SwiftUI

struct MissionInboxView: View {
    @ObservedObject var viewModel: MissionInboxViewModel
    let onCreateMission: () -> Void
    let onSelectMission: (MobileMission) -> Void
    let onSignOut: () -> Void

    var body: some View {
        List(viewModel.missions) { mission in
            Button {
                onSelectMission(mission)
            } label: {
                VStack(alignment: .leading, spacing: 6) {
                    HStack {
                        Text(mission.title)
                            .font(.headline)
                        Spacer()
                        StatusBadge(status: mission.status)
                    }
                    Text(mission.summary)
                        .font(.subheadline)
                        .foregroundStyle(.secondary)
                }
                .padding(.vertical, 4)
            }
            .buttonStyle(.plain)
        }
        .navigationTitle("Missions")
        .toolbar {
            Button("New") {
                onCreateMission()
            }
            Button("Sign Out") {
                onSignOut()
            }
        }
        .task { await viewModel.load() }
        .refreshable { await viewModel.load() }
    }
}
