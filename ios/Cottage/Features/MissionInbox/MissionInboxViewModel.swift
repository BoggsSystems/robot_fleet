import Foundation

@MainActor
final class MissionInboxViewModel: ObservableObject {
    @Published var missions: [MobileMission] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let missionService: MissionServiceProtocol

    init(missionService: MissionServiceProtocol) {
        self.missionService = missionService
    }

    func load() async {
        errorMessage = nil
        isLoading = true
        defer { isLoading = false }

        do {
            missions = try await missionService.fetchMissions()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
