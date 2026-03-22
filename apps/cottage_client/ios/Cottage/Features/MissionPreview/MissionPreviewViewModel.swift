import Foundation

@MainActor
final class MissionPreviewViewModel: ObservableObject {
    @Published var isConfirming = false
    @Published var errorMessage: String?
    @Published var confirmedMission: MobileMission?

    let previewResponse: MissionPreviewResponse
    private let missionService: MissionServiceProtocol

    init(previewResponse: MissionPreviewResponse, missionService: MissionServiceProtocol) {
        self.previewResponse = previewResponse
        self.missionService = missionService
    }

    func confirmMission() async {
        errorMessage = nil
        isConfirming = true
        defer { isConfirming = false }

        do {
            let response = try await missionService.confirmMission(
                missionID: previewResponse.mission.id,
                confirmedBy: "operator@local"
            )
            confirmedMission = response.mission
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
