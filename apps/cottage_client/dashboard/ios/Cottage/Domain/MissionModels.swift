import Foundation

enum MissionStatus: String, Codable, CaseIterable {
    case clarificationRequired = "clarification_required"
    case previewReady = "preview_ready"
    case approved
    case planned
    case dispatched
    case inProgress = "in_progress"
    case paused
    case completed
    case blocked
    case cancelled

    var displayName: String {
        switch self {
        case .clarificationRequired:
            return "Clarification Needed"
        case .previewReady:
            return "Preview Ready"
        case .planned:
            return "Planned"
        case .approved:
            return "Approved"
        case .dispatched:
            return "Dispatched"
        case .inProgress:
            return "In Progress"
        case .paused:
            return "Paused"
        case .completed:
            return "Completed"
        case .blocked:
            return "Blocked"
        case .cancelled:
            return "Cancelled"
        }
    }
}

struct MissionQuestion: Codable, Equatable {
    let missionID: String
    let prompt: String
    let fieldName: String
    let reason: String

    enum CodingKeys: String, CodingKey {
        case missionID = "mission_id"
        case prompt
        case fieldName = "field_name"
        case reason
    }
}

struct MobileMission: Codable, Equatable, Identifiable {
    let id: String
    let title: String
    let requestText: String
    let status: MissionStatus
    let missionType: String
    let from: String?
    let to: String?
    let assignedRobotID: String?
    let taskCount: Int
    let taskIDs: [String]
    let clarificationRequired: Bool
    let clarificationQuestion: MissionQuestion?
    let summary: String
    let currentStep: String?
    let currentTaskID: String?
    let completedSteps: Int
    let totalSteps: Int
    let fallbackAvailable: Bool
    let fallbackRobotIDs: [String]
    let blockedReason: String?
    let approvalRequired: Bool
    let approvalStatus: String
    let replanAvailable: Bool
    let createdAt: String
    let updatedAt: String

    enum CodingKeys: String, CodingKey {
        case id = "missionId"
        case title
        case requestText
        case status
        case missionType
        case from
        case to
        case assignedRobotID = "assignedRobotId"
        case taskCount
        case taskIDs = "taskIds"
        case clarificationRequired
        case clarificationQuestion
        case summary
        case currentStep
        case currentTaskID = "currentTaskId"
        case completedSteps
        case totalSteps
        case fallbackAvailable
        case fallbackRobotIDs = "fallbackRobotIds"
        case blockedReason
        case approvalRequired
        case approvalStatus
        case replanAvailable
        case createdAt
        case updatedAt
    }
}

struct MissionPreviewIntent: Codable, Equatable {
    let missionID: String
    let missionType: String
    let objective: String
    let sourceZone: String?
    let destinationZone: String?
    let cargoType: String?
    let priority: String
    let requiredCapabilities: [String]
    let humanConfirmationRequired: Bool

    enum CodingKeys: String, CodingKey {
        case missionID = "mission_id"
        case missionType = "mission_type"
        case objective
        case sourceZone = "source_zone"
        case destinationZone = "destination_zone"
        case cargoType = "cargo_type"
        case priority
        case requiredCapabilities = "required_capabilities"
        case humanConfirmationRequired = "human_confirmation_required"
    }
}

struct MissionPreviewPlan: Codable, Equatable {
    let missionID: String
    let missionType: String
    let status: String
    let explanation: String

    enum CodingKeys: String, CodingKey {
        case missionID = "mission_id"
        case missionType = "mission_type"
        case status
        case explanation
    }
}

struct MissionProposalCandidateAllocation: Codable, Equatable, Identifiable {
    let robotID: String
    let displayName: String
    let robotType: String
    let score: Double
    let rationale: String

    var id: String { robotID }

    enum CodingKeys: String, CodingKey {
        case robotID = "robot_id"
        case displayName = "display_name"
        case robotType = "robot_type"
        case score
        case rationale
    }
}

struct MissionProposalStep: Codable, Equatable, Identifiable {
    let id: String
    let summary: String
    let taskType: String
    let dependsOn: [String]
    let targetZone: String?
    let estimatedDurationMinutes: Double?
    let routeLabels: [String]
    let candidateAllocations: [MissionProposalCandidateAllocation]

    enum CodingKeys: String, CodingKey {
        case id = "task_id"
        case summary
        case taskType = "task_type"
        case dependsOn = "depends_on"
        case targetZone = "target_zone"
        case estimatedDurationMinutes = "estimated_duration_minutes"
        case routeLabels = "route_labels"
        case candidateAllocations = "candidate_allocations"
    }
}

struct MissionProposalPlan: Codable, Equatable {
    let summary: String?
    let candidateSteps: [MissionProposalStep]
    let operatorNotes: [String]

    enum CodingKeys: String, CodingKey {
        case summary
        case candidateSteps = "candidate_steps"
        case operatorNotes = "operator_notes"
    }
}

struct MissionProposal: Codable, Equatable {
    let missionID: String
    let status: String
    let provider: String?
    let warnings: [String]
    let assumptions: [String]
    let generatedAt: String?
    let plan: MissionProposalPlan?

    enum CodingKeys: String, CodingKey {
        case missionID = "missionId"
        case status
        case provider
        case warnings
        case assumptions
        case generatedAt
        case plan
    }
}

struct ValidatedPlan: Codable, Equatable {
    let missionID: String
    let status: String
    let executable: Bool
    let missionType: String?
    let warnings: [String]
    let blockingReasons: [String]
    let explanation: String?

    enum CodingKeys: String, CodingKey {
        case missionID = "missionId"
        case status
        case executable
        case missionType
        case warnings
        case blockingReasons
        case explanation
    }
}

struct ApprovalDecision: Codable, Equatable {
    let missionID: String
    let required: Bool
    let status: String
    let decision: String?
    let approvedBy: String?
    let approvedAt: String?
    let notes: String?

    enum CodingKeys: String, CodingKey {
        case missionID = "missionId"
        case required
        case status
        case decision
        case approvedBy
        case approvedAt
        case notes
    }
}

struct ReplanProposal: Codable, Equatable {
    let missionID: String
    let status: String
    let action: String
    let summary: String
    let reason: String
    let provider: String?
    let reviewSummary: String?
    let taskID: String?
    let taskSummary: String?
    let candidateRobotIDs: [String]
    let routeNodes: [String]
    let routeLabels: [String]
    let operatorNotes: [String]
    let warnings: [String]
    let generatedAt: String?
    let requestedBy: String?

    enum CodingKeys: String, CodingKey {
        case missionID = "missionId"
        case status
        case action
        case summary
        case reason
        case provider
        case reviewSummary
        case taskID = "taskId"
        case taskSummary
        case candidateRobotIDs = "candidateRobotIds"
        case routeNodes = "routeNodes"
        case routeLabels = "routeLabels"
        case operatorNotes
        case warnings
        case generatedAt
        case requestedBy
    }
}

struct MissionPreviewPayload: Codable, Equatable {
    let status: String
    let intentProvider: String?
    let question: MissionQuestion?
    let intent: MissionPreviewIntent?
    let plan: MissionPreviewPlan?

    enum CodingKeys: String, CodingKey {
        case status
        case intentProvider = "intent_provider"
        case question
        case intent
        case plan
    }
}

struct MissionEvent: Codable, Equatable, Identifiable {
    let id: String
    let time: String
    let message: String
    let tone: String
    let taskID: String?
    let status: String?

    enum CodingKeys: String, CodingKey {
        case id
        case time
        case message
        case tone
        case taskID = "task_id"
        case status
    }
}

struct MissionPreviewResponse: Codable, Equatable {
    let mission: MobileMission
    let preview: MissionPreviewPayload
}

struct MissionListResponse: Codable, Equatable {
    let missions: [MobileMission]
}

struct MissionDetailResponse: Codable, Equatable {
    let mission: MobileMission
    let preview: MissionPreviewPayload
    let request: MissionRequestRecord?
    let proposal: MissionProposal?
    let validatedPlan: ValidatedPlan?
    let approval: ApprovalDecision?
    let replan: ReplanProposal?
    let events: [MissionEvent]
}

struct MissionRequestRecord: Codable, Equatable {
    let missionID: String
    let requestText: String
    let requestedBy: String
    let context: [String: String]?
    let submittedAt: String
    let status: String

    enum CodingKeys: String, CodingKey {
        case missionID = "missionId"
        case requestText
        case requestedBy
        case context
        case submittedAt
        case status
    }
}

struct MissionDispatch: Codable, Equatable {
    let status: String
}

struct MissionConfirmResponse: Codable, Equatable {
    let mission: MobileMission
    let dispatch: MissionDispatch?
}

struct MissionPreviewRequest: Encodable, Equatable {
    let requestText: String
    let requestedBy: String
    let context: [String: String]
}

struct MissionClarificationRequest: Encodable, Equatable {
    let answer: String
}

struct MissionConfirmRequest: Encodable, Equatable {
    let confirmedBy: String
}

struct MissionApprovalRequest: Encodable, Equatable {
    let approvedBy: String
}

struct MissionControlRequest: Encodable, Equatable {
    let requestedBy: String
}
