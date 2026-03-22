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
            currentStep: status == .clarificationRequired ? nil : "Stage groceries at dock for transfer",
            currentTaskID: status == .clarificationRequired ? nil : "task-preview-1",
            completedSteps: status == .inProgress ? 1 : 0,
            totalSteps: status == .clarificationRequired ? 0 : 3,
            fallbackAvailable: status == .blocked,
            fallbackRobotIDs: status == .blocked ? ["carrier-03"] : [],
            blockedReason: status == .blocked ? "Carrier fault on dock transfer." : nil,
            approvalRequired: true,
            approvalStatus: status == .previewReady ? "pending" : (status == .cancelled ? "cancelled" : "approved"),
            replanAvailable: status == .blocked,
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

    static func sampleEvents() -> [MissionEvent] {
        [
            MissionEvent(
                id: "evt-1",
                time: "2026-03-19T12:00:00Z",
                message: "Stage groceries at dock for transfer assigned to carrier-01.",
                tone: "live",
                taskID: "task-preview-1",
                status: "assigned"
            ),
            MissionEvent(
                id: "evt-2",
                time: "2026-03-19T12:01:10Z",
                message: "Mission in progress: Bring groceries from dock to kitchen",
                tone: "live",
                taskID: nil,
                status: "in_progress"
            ),
        ]
    }

    static func sampleProposal(missionID: String = "msn-preview-1") -> MissionProposal {
        MissionProposal(
            missionID: missionID,
            status: "candidate",
            provider: "local-proposal",
            warnings: ["No candidate robot is currently available for 'Stage groceries at dock for transfer'."],
            assumptions: ["Route from dock to kitchen remains traversable.", "Cargo is staged and accessible for pickup at the source zone."],
            generatedAt: "2026-03-19T00:00:00Z",
            plan: MissionProposalPlan(
                summary: "Mission decomposed into 3 staged tasks covering pickup, transfer, and final delivery.",
                candidateSteps: [
                    MissionProposalStep(
                        id: "task-preview-1",
                        summary: "Stage groceries at dock for transfer",
                        taskType: "pickup",
                        dependsOn: [],
                        targetZone: "dock",
                        estimatedDurationMinutes: 4,
                        routeLabels: ["Main Dock"],
                        candidateAllocations: []
                    ),
                    MissionProposalStep(
                        id: "task-preview-2",
                        summary: "Transfer groceries from dock to entry",
                        taskType: "transport",
                        dependsOn: ["task-preview-1"],
                        targetZone: "entry",
                        estimatedDurationMinutes: 7,
                        routeLabels: ["Main Dock", "Dock Walkway", "Square Dock Area", "Narrow Walkway", "Island Path Entry", "Natural Cottage Path", "Deck Stairs", "Deck", "Screened Dining Area", "Entry Foyer"],
                        candidateAllocations: []
                    ),
                    MissionProposalStep(
                        id: "task-preview-3",
                        summary: "Complete indoor delivery of groceries to kitchen",
                        taskType: "handoff_delivery",
                        dependsOn: ["task-preview-2"],
                        targetZone: "kitchen",
                        estimatedDurationMinutes: 6,
                        routeLabels: ["Entry Foyer", "Dining Room", "Kitchen"],
                        candidateAllocations: [
                            MissionProposalCandidateAllocation(
                                robotID: "carrier-02",
                                displayName: "Carrier 02",
                                robotType: "humanoid",
                                score: 2.13,
                                rationale: "Carrier 02 is idle, already positioned at entry, and supports fine manipulation."
                            )
                        ]
                    )
                ],
                operatorNotes: ["Indoor handoff should use the humanoid for final placement."]
            )
        )
    }

    static func sampleValidatedPlan(missionID: String = "msn-preview-1", executable: Bool = false) -> ValidatedPlan {
        ValidatedPlan(
            missionID: missionID,
            status: executable ? "planned" : "blocked",
            executable: executable,
            missionType: "cargo_transfer",
            warnings: executable ? [] : ["Task 'Complete indoor delivery of groceries to Kitchen' has no configured fallback robot."],
            blockingReasons: executable ? [] : [
                "Task 'Stage groceries at dock for transfer' has no allocatable robot candidate.",
                "Task 'Transfer groceries from dock to entry' has no allocatable robot candidate."
            ],
            explanation: executable ? "Validated plan is executable." : "Validated plan is blocked until the outdoor steps have viable robot candidates."
        )
    }

    static func sampleApproval(missionID: String = "msn-preview-1", status: String = "pending") -> ApprovalDecision {
        ApprovalDecision(
            missionID: missionID,
            required: true,
            status: status,
            decision: status == "approved" ? "approved" : nil,
            approvedBy: status == "approved" ? "operator@local" : nil,
            approvedAt: status == "approved" ? "2026-03-19T00:01:00Z" : nil,
            notes: nil
        )
    }

    static func sampleReplan(missionID: String = "msn-preview-1") -> ReplanProposal {
        ReplanProposal(
            missionID: missionID,
            status: "candidate",
            action: "use_fallback",
            summary: "Reassign Stage groceries at dock for transfer to the best available fallback robot.",
            reason: "Carrier fault on dock transfer.",
            provider: "local-replan",
            reviewSummary: "Execution issue detected: Carrier fault on dock transfer. Proposed fallback keeps the current mission structure and swaps execution to another robot.",
            taskID: "task-preview-1",
            taskSummary: "Stage groceries at dock for transfer",
            candidateRobotIDs: ["carrier-03"],
            routeNodes: [],
            routeLabels: [],
            operatorNotes: ["Fallback reassignment preserves the existing step order and mission dependencies."],
            warnings: [],
            generatedAt: "2026-03-19T00:02:00Z",
            requestedBy: "operator@local"
        )
    }
}
