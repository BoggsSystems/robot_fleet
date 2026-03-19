import Foundation

enum PreviewFixtures {
    static func sampleMission(id: String = "msn-preview-1", status: MissionStatus = .previewReady) -> MobileMission {
        MobileMission(
            id: id,
            title: "Bring groceries from dock to kitchen",
            requestText: "Bring groceries from dock to kitchen",
            status: status,
            missionType: "cargo_transfer",
            from: "dock",
            to: "kitchen",
            assignedRobotID: status == .clarificationRequired ? nil : "carrier-01",
            taskCount: 1,
            taskIDs: status == .clarificationRequired ? [] : ["task-preview-1"],
            clarificationRequired: status == .clarificationRequired,
            clarificationQuestion: status == .clarificationRequired
                ? MissionQuestion(
                    missionID: id,
                    prompt: "Which area should the mission start from?",
                    fieldName: "source_zone",
                    reason: "Source zone missing."
                )
                : nil,
            summary: status == .clarificationRequired
                ? "The mission needs one more detail before it can be planned."
                : "Carrier 01 can handle this transfer now.",
            createdAt: "2026-03-19T00:00:00Z",
            updatedAt: "2026-03-19T00:00:00Z"
        )
    }

    static func previewPayload(status: MissionStatus, missionID: String = "msn-preview-1") -> MissionPreviewPayload {
        MissionPreviewPayload(
            status: status == .clarificationRequired ? "clarification_required" : "ok",
            intentProvider: "local-rule-parser",
            question: status == .clarificationRequired ? sampleMission(id: missionID, status: status).clarificationQuestion : nil,
            intent: MissionPreviewIntent(
                missionID: missionID,
                missionType: "cargo_transfer",
                objective: "Bring groceries from dock to kitchen",
                sourceZone: "dock",
                destinationZone: "kitchen",
                cargoType: "groceries",
                priority: "normal",
                requiredCapabilities: ["cargo_transport", "indoor_delivery"],
                humanConfirmationRequired: false
            ),
            plan: MissionPreviewPlan(
                missionID: missionID,
                missionType: "cargo_transfer",
                status: "planned",
                explanation: "Mission preview generated."
            )
        )
    }

    static func previewResponse(status: MissionStatus, missionID: String = "msn-preview-1") -> MissionPreviewResponse {
        MissionPreviewResponse(
            mission: sampleMission(id: missionID, status: status),
            preview: previewPayload(status: status, missionID: missionID)
        )
    }
}
