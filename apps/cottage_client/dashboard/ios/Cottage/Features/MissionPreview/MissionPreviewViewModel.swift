import Foundation

@MainActor
final class MissionPreviewViewModel: ObservableObject {
    @Published var isConfirming = false
    @Published var errorMessage: String?
    @Published var confirmedMission: MobileMission?
    @Published var detailResponse: MissionDetailResponse?

    let previewResponse: MissionPreviewResponse
    private let missionService: MissionServiceProtocol

    init(previewResponse: MissionPreviewResponse, missionService: MissionServiceProtocol) {
        self.previewResponse = previewResponse
        self.missionService = missionService
    }

    func loadDetailIfNeeded() async {
        guard detailResponse == nil else { return }
        do {
            detailResponse = try await missionService.fetchMission(missionID: previewResponse.mission.id)
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func approveMission() async {
        errorMessage = nil
        isConfirming = true
        defer { isConfirming = false }

        do {
            let response = try await missionService.approveMission(
                missionID: previewResponse.mission.id,
                approvedBy: "operator@local"
            )
            confirmedMission = response.mission
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
