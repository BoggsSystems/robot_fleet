import Foundation

protocol MissionServiceProtocol {
    func previewMission(text: String, requestedBy: String) async throws -> MissionPreviewResponse
    func clarifyMission(missionID: String, answer: String) async throws -> MissionPreviewResponse
    func approveMission(missionID: String, approvedBy: String) async throws -> MissionConfirmResponse
    func dispatchMission(missionID: String, confirmedBy: String) async throws -> MissionConfirmResponse
    func pauseMission(missionID: String, requestedBy: String) async throws -> MobileMission
    func resumeMission(missionID: String, requestedBy: String) async throws -> MobileMission
    func retryMission(missionID: String, requestedBy: String) async throws -> MobileMission
    func previewReplan(missionID: String, requestedBy: String) async throws -> MobileMission
    func applyReplan(missionID: String, requestedBy: String) async throws -> MobileMission
    func useFallbackMission(missionID: String, requestedBy: String) async throws -> MobileMission
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

    func approveMission(missionID: String, approvedBy: String) async throws -> MissionConfirmResponse {
        try await apiClient.post(
            "api/mobile/missions/\(missionID)/approve",
            body: MissionApprovalRequest(approvedBy: approvedBy),
            responseType: MissionConfirmResponse.self
        )
    }

    func dispatchMission(missionID: String, confirmedBy: String) async throws -> MissionConfirmResponse {
        try await apiClient.post(
            "api/mobile/missions/\(missionID)/dispatch",
            body: MissionConfirmRequest(confirmedBy: confirmedBy),
            responseType: MissionConfirmResponse.self
        )
    }

    func pauseMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        try await missionControl(path: "api/mobile/missions/\(missionID)/pause", requestedBy: requestedBy)
    }

    func resumeMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        try await missionControl(path: "api/mobile/missions/\(missionID)/resume", requestedBy: requestedBy)
    }

    func retryMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        try await missionControl(path: "api/mobile/missions/\(missionID)/retry", requestedBy: requestedBy)
    }

    func previewReplan(missionID: String, requestedBy: String) async throws -> MobileMission {
        try await missionControl(path: "api/mobile/missions/\(missionID)/replan-preview", requestedBy: requestedBy)
    }

    func applyReplan(missionID: String, requestedBy: String) async throws -> MobileMission {
        try await missionControl(path: "api/mobile/missions/\(missionID)/replan-apply", requestedBy: requestedBy)
    }

    func useFallbackMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        try await missionControl(path: "api/mobile/missions/\(missionID)/fallback", requestedBy: requestedBy)
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

    private func missionControl(path: String, requestedBy: String) async throws -> MobileMission {
        struct MissionControlResponse: Decodable { let mission: MobileMission }
        let response = try await apiClient.post(
            path,
            body: MissionControlRequest(requestedBy: requestedBy),
            responseType: MissionControlResponse.self
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

    func approveMission(missionID: String, approvedBy: String) async throws -> MissionConfirmResponse {
        MissionConfirmResponse(
            mission: PreviewFixtures.sampleMission(id: missionID, status: .approved),
            dispatch: nil
        )
    }

    func dispatchMission(missionID: String, confirmedBy: String) async throws -> MissionConfirmResponse {
        MissionConfirmResponse(
            mission: PreviewFixtures.sampleMission(id: missionID, status: .inProgress),
            dispatch: MissionDispatch(status: "ok")
        )
    }

    func pauseMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .paused)
    }

    func resumeMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .inProgress)
    }

    func retryMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .inProgress)
    }

    func previewReplan(missionID: String, requestedBy: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .blocked)
    }

    func applyReplan(missionID: String, requestedBy: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .inProgress)
    }

    func useFallbackMission(missionID: String, requestedBy: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .inProgress)
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
            preview: PreviewFixtures.previewPayload(status: .previewReady, missionID: missionID),
            request: MissionRequestRecord(
                missionID: missionID,
                requestText: "Bring groceries from dock to kitchen",
                requestedBy: "operator@local",
                context: ["source": "preview"],
                submittedAt: "2026-03-19T00:00:00Z",
                status: "submitted"
            ),
            proposal: PreviewFixtures.sampleProposal(missionID: missionID),
            validatedPlan: PreviewFixtures.sampleValidatedPlan(missionID: missionID, executable: false),
            approval: PreviewFixtures.sampleApproval(missionID: missionID, status: "pending"),
            replan: PreviewFixtures.sampleReplan(missionID: missionID),
            events: PreviewFixtures.sampleEvents()
        )
    }

    func cancelMission(missionID: String) async throws -> MobileMission {
        PreviewFixtures.sampleMission(id: missionID, status: .cancelled)
    }
}

private struct EmptyBody: Encodable {}
