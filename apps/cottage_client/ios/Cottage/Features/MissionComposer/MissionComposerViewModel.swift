import Foundation

@MainActor
final class MissionComposerViewModel: ObservableObject {
    @Published var requestText = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var previewResponse: MissionPreviewResponse?

    let missionService: MissionServiceProtocol

    init(missionService: MissionServiceProtocol) {
        self.missionService = missionService
    }

    func previewMission() async {
        errorMessage = nil
        isLoading = true
        defer { isLoading = false }

        do {
            previewResponse = try await missionService.previewMission(text: requestText, requestedBy: "operator@local")
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
