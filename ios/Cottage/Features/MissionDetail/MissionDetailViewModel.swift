import Foundation

@MainActor
final class MissionDetailViewModel: ObservableObject {
    @Published var mission: MobileMission?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let missionID: String
    private let missionService: MissionServiceProtocol

    init(missionID: String, missionService: MissionServiceProtocol) {
        self.missionID = missionID
        self.missionService = missionService
    }

    func load() async {
        errorMessage = nil
        isLoading = true
        defer { isLoading = false }

        do {
            let response = try await missionService.fetchMission(missionID: missionID)
            mission = response.mission
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func cancelMission() async {
        errorMessage = nil
        do {
            mission = try await missionService.cancelMission(missionID: missionID)
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
