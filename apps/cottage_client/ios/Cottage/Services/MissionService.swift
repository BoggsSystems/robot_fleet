import Foundation

protocol MissionServiceProtocol {
    func previewMission(text: String, requestedBy: String) async throws -> MissionPreviewResponse
    func clarifyMission(missionID: String, answer: String) async throws -> MissionPreviewResponse
    func confirmMission(missionID: String, confirmedBy: String) async throws -> MissionConfirmResponse
    func fetchMissions() async throws -> [MobileMission]
    func fetchMission(missionID: String) async throws -> MissionDetailResponse
    func cancelMission(missionID: String) async throws -> MobileMission
}

struct MissionServiceLive: MissionServiceProtocol {
    let apiClient: APIClientProtocol

    func previewMission(text: String, requestedBy: String) async throws -> MissionPreviewResponse {
        try await apiClient.post(
            "api/mobile/missions/preview",
            body: MissionPreviewRequest(requestText: text, requestedBy: requestedBy, context: [:]),
            responseType: MissionPreviewResponse.self
        )
    }

    func clarifyMission(missionID: String, answer: String) async throws -> MissionPreviewResponse {
        try await apiClient.post(
            "api/mobile/missions/\(missionID)/clarify",
            body: MissionClarificationRequest(answer: answer),
            responseType: MissionPreviewResponse.self
        )
    }

    func confirmMission(missionID: String, confirmedBy: String) async throws -> MissionConfirmResponse {
        try await apiClient.post(
            "api/mobile/missions/\(missionID)/confirm",
            body: MissionConfirmRequest(confirmedBy: confirmedBy),
            responseType: MissionConfirmResponse.self
        )
    }

    func fetchMissions() async throws -> [MobileMission] {
        let response = try await apiClient.get("api/mobile/missions", responseType: MissionListResponse.self)
        return response.missions
    }

    func fetchMission(missionID: String) async throws -> MissionDetailResponse {
        try await apiClient.get("api/mobile/missions/\(missionID)", responseType: MissionDetailResponse.self)
    }

    func cancelMission(missionID: String) async throws -> MobileMission {
        struct CancelResponse: Decodable { let mission: MobileMission }
        let response = try await apiClient.post(
            "api/mobile/missions/\(missionID)/cancel",
            body: EmptyBody(),
            responseType: CancelResponse.self
        )
        return response.mission
    }
}

struct MissionServiceMock: MissionServiceProtocol {
    func previewMission(text: String, requestedBy: String) async throws -> MissionPreviewResponse {
        PreviewFixtures.previewResponse(status: text.lowercased().contains("inside") ? .clarificationRequired : .previewReady)
    }

    func clarifyMission(missionID: String, answer: String) async throws -> MissionPreviewResponse {
        PreviewFixtures.previewResponse(status: .previewReady, missionID: missionID)
    }

    func confirmMission(missionID: String, confirmedBy: String) async throws -> MissionConfirmResponse {
        MissionConfirmResponse(
            mission: PreviewFixtures.sampleMission(id: missionID, status: .inProgress),
            dispatch: MissionDispatch(status: "ok")
        )
    }

    func fetchMissions() async throws -> [MobileMission] {
        [
            PreviewFixtures.sampleMission(id: "msn-preview-1", status: .previewReady),
            PreviewFixtures.sampleMission(id: "msn-live-2", status: .inProgress)
        ]
    }

    func fetchMission(missionID: String) async throws -> MissionDetailResponse {
        MissionDetailResponse(
            mission: PreviewFixtures.sampleMission(id: missionID, status: .inProgress),
            preview: PreviewFixtures.previewPayload(status: .previewReady, missionID: missionID)
        )
    }

    func cancelMission(missionID: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .cancelled)
    }
}

private struct EmptyBody: Encodable {}
