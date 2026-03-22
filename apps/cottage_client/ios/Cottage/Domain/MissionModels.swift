import Foundation

enum MissionStatus: String, Codable, CaseIterable {
    case clarificationRequired = "clarification_required"
    case previewReady = "preview_ready"
    case planned
    case dispatched
    case inProgress = "in_progress"
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
        case .dispatched:
            return "Dispatched"
        case .inProgress:
            return "In Progress"
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
