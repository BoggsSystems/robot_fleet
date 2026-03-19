import Foundation

@MainActor
final class MissionClarificationViewModel: ObservableObject {
    @Published var answer = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var updatedPreview: MissionPreviewResponse?

    let mission: MobileMission
    private let missionService: MissionServiceProtocol

    init(mission: MobileMission, missionService: MissionServiceProtocol) {
        self.mission = mission
        self.missionService = missionService
    }

    func submitClarification() async {
        errorMessage = nil
        isLoading = true
        defer { isLoading = false }

        do {
            updatedPreview = try await missionService.clarifyMission(missionID: mission.id, answer: answer)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
