import Foundation

// MARK: - Robot Management Models

struct RobotConfig: Codable, Equatable, Identifiable {
    let id: String
    let robotId: String
    let name: String
    let ipAddress: String
    let networkInterface: String
    let capabilities: [String]
    let robotType: String
    let robotCategory: String
    let vendor: String
    let model: String
    let serial: String
    let firmware: String
    let zone: String?
    let subZone: String?
    let status: String
    let batteryLevel: Float?
    let payloadCapacityKg: Float?
    let metadata: [String: Any]
    
    var identifier: String { robotId }
    
    enum CodingKeys: String, CodingKey {
        case id
        case robotId = "robot_id"
        case name = "name"
        case ipAddress = "ip_address"
        case networkInterface = "network_interface"
        case capabilities = "capabilities"
        case robotType = "robot_type"
        case robotCategory = "robot_category"
        case vendor = "vendor"
        case model = "model"
        case serial = "serial"
        case firmware = "firmware"
        case zone = "zone"
        case subZone = "sub_zone"
        case status = "status"
        case batteryLevel = "battery_level"
        case payloadCapacityKg = "payload_capacity_kg"
        case metadata = "metadata"
    }
    
    // Custom decoding to handle Any type for metadata
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        id = try container.decodeIfPresent(String.self, forKey: .id) ?? UUID().uuidString
        robotId = try container.decode(String.self, forKey: .robotId)
        name = try container.decode(String.self, forKey: .name)
        ipAddress = try container.decode(String.self, forKey: .ipAddress)
        networkInterface = try container.decode(String.self, forKey: .networkInterface)
        capabilities = try container.decode([String].self, forKey: .capabilities)
        robotType = try container.decode(String.self, forKey: .robotType)
        robotCategory = try container.decode(String.self, forKey: .robotCategory)
        vendor = try container.decode(String.self, forKey: .vendor)
        model = try container.decode(String.self, forKey: .model)
        serial = try container.decode(String.self, forKey: .serial)
        firmware = try container.decode(String.self, forKey: .firmware)
        zone = try container.decodeIfPresent(String.self, forKey: .zone)
        subZone = try container.decodeIfPresent(String.self, forKey: .subZone)
        status = try container.decode(String.self, forKey: .status)
        batteryLevel = try container.decodeIfPresent(Float.self, forKey: .batteryLevel)
        payloadCapacityKg = try container.decodeIfPresent(Float.self, forKey: .payloadCapacityKg)
        
        // Handle metadata decoding
        if let metadataData = try? container.decodeIfPresent(Data.self, forKey: .metadata),
           let metadataObject = try? JSONSerialization.jsonObject(with: metadataData) as? [String: Any] {
            metadata = metadataObject
        } else {
            metadata = [:]
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(id, forKey: .id)
        try container.encode(robotId, forKey: .robotId)
        try container.encode(name, forKey: .name)
        try container.encode(ipAddress, forKey: .ipAddress)
        try container.encode(networkInterface, forKey: .networkInterface)
        try container.encode(capabilities, forKey: .capabilities)
        try container.encode(robotType, forKey: .robotType)
        try container.encode(robotCategory, forKey: .robotCategory)
        try container.encode(vendor, forKey: .vendor)
        try container.encode(model, forKey: .model)
        try container.encode(serial, forKey: .serial)
        try container.encode(firmware, forKey: .firmware)
        try container.encodeIfPresent(zone, forKey: .zone)
        try container.encodeIfPresent(subZone, forKey: .subZone)
        try container.encode(status, forKey: .status)
        try container.encodeIfPresent(batteryLevel, forKey: .batteryLevel)
        try container.encodeIfPresent(payloadCapacityKg, forKey: .payloadCapacityKg)
        
        // Handle metadata encoding
        if let metadataData = try? JSONSerialization.data(withJSONObject: metadata) {
            try container.encode(metadataData, forKey: .metadata)
        }
    }
}

struct RobotRegistrationResponse: Codable, Equatable {
    let success: Bool
    let message: String
    let robot: RobotConfig
    let onboarding: OnboardingStatus
}

struct OnboardingStatus: Codable, Equatable {
    let robotId: String
    let stage: String
    let status: String
    let details: [String: Any]
    let createdAt: String
    let updatedAt: String
    
    enum CodingKeys: String, CodingKey {
        case robotId = "robot_id"
        case stage = "stage"
        case status = "status"
        case details = "details"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        robotId = try container.decode(String.self, forKey: .robotId)
        stage = try container.decode(String.self, forKey: .stage)
        status = try container.decode(String.self, forKey: .status)
        createdAt = try container.decode(String.self, forKey: .createdAt)
        updatedAt = try container.decode(String.self, forKey: .updatedAt)
        
        if let detailsData = try? container.decodeIfPresent(Data.self, forKey: .details),
           let detailsObject = try? JSONSerialization.jsonObject(with: detailsData) as? [String: Any] {
            details = detailsObject
        } else {
            details = [:]
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(robotId, forKey: .robotId)
        try container.encode(stage, forKey: .stage)
        try container.encode(status, forKey: .status)
        try container.encode(createdAt, forKey: .createdAt)
        try container.encode(updatedAt, forKey: .updatedAt)
        
        if let detailsData = try? JSONSerialization.data(withJSONObject: details) {
            try container.encode(detailsData, forKey: .details)
        }
    }
}

struct OnboardingUpdateRequest: Codable, Equatable {
    let stage: String
    let status: String
    let details: String
}

struct RobotConnectionTest: Codable, Equatable {
    let ipAddress: String
    let networkInterface: String?
}

struct RobotConnectionResponse: Codable, Equatable {
    let success: Bool
    let model: String
    let serial: String
    let firmware: String
    let battery: Float
    let message: String
}

struct RobotStatusUpdate: Codable, Equatable {
    let status: String
    let zoneId: String?
    let capabilities: [String]?
    let metadataUpdates: [String: Any]?
    
    enum CodingKeys: String, CodingKey {
        case status = "status"
        case zoneId = "zone_id"
        case capabilities = "capabilities"
        case metadataUpdates = "metadata_updates"
    }
    
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        
        status = try container.decode(String.self, forKey: .status)
        zoneId = try container.decodeIfPresent(String.self, forKey: .zoneId)
        capabilities = try container.decodeIfPresent([String].self, forKey: .capabilities)
        
        if let metadataData = try? container.decodeIfPresent(Data.self, forKey: .metadataUpdates),
           let metadataObject = try? JSONSerialization.jsonObject(with: metadataData) as? [String: Any] {
            metadataUpdates = metadataObject
        } else {
            metadataUpdates = nil
        }
    }
    
    func encode(to encoder: Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        
        try container.encode(status, forKey: .status)
        try container.encodeIfPresent(zoneId, forKey: .zoneId)
        try container.encodeIfPresent(capabilities, forKey: .capabilities)
        
        if let metadataUpdates = metadataUpdates,
           let metadataData = try? JSONSerialization.data(withJSONObject: metadataUpdates) {
            try container.encode(metadataData, forKey: .metadataUpdates)
        }
    }
}

struct RobotListResponse: Codable, Equatable {
    let robots: [RobotConfig]
    let total: Int
    let available: Int
}

struct CalibrationRequest: Codable, Equatable {
    let robotId: String
    let calibrationType: String
    
    enum CodingKeys: String, CodingKey {
        case robotId = "robot_id"
        case calibrationType = "calibration_type"
    }
}

struct CalibrationResponse: Codable, Equatable {
    let success: Bool
    let stage: String
    let status: String
    let details: String
}

// MARK: - Robot Status and Types

enum RobotStatus: String, Codable, CaseIterable {
    case idle = "idle"
    case availableSoon = "available_soon"
    case busy = "busy"
    case charging = "charging"
    case degraded = "degraded"
    case maintenance = "maintenance"
    case offline = "offline"
    case reserved = "reserved"
    
    var displayName: String {
        switch self {
        case .idle:
            return "Idle"
        case .availableSoon:
            return "Available Soon"
        case .busy:
            return "Busy"
        case .charging:
            return "Charging"
        case .degraded:
            return "Degraded"
        case .maintenance:
            return "Maintenance"
        case .offline:
            return "Offline"
        case .reserved:
            return "Reserved"
        }
    }
    
    var isAvailable: Bool {
        switch self {
        case .idle, .availableSoon:
            return true
        default:
            return false
        }
    }
    
    var color: Color {
        switch self {
        case .idle, .availableSoon:
            return .green
        case .busy, .reserved:
            return .blue
        case .charging:
            return .orange
        case .degraded, .maintenance, .offline:
            return .red
        }
    }
}

enum RobotType: String, Codable, CaseIterable {
    case humanoid = "humanoid"
    case cargo = "cargo"
    case quadruped = "quadruped"
    case drone = "drone"
    case boat = "boat"
    case unknown = "unknown"
    
    var displayName: String {
        switch self {
        case .humanoid:
            return "Humanoid"
        case .cargo:
            return "Cargo Robot"
        case .quadruped:
            return "Quadruped"
        case .drone:
            return "Drone"
        case .boat:
            return "Boat"
        case .unknown:
            return "Unknown"
        }
    }
    
    var icon: String {
        switch self {
        case .humanoid:
            return "🤖"
        case .cargo:
            return "🚚"
        case .quadruped:
            return "🐕"
        case .drone:
            return "🚁"
        case .boat:
            return "⛵"
        case .unknown:
            return "❓"
        }
    }
}

enum OnboardingStage: String, Codable, CaseIterable {
    case discovery = "discovery"
    case identity = "identity"
    case calibration = "calibration"
    case validation = "validation"
    case completed = "completed"
    
    var displayName: String {
        switch self {
        case .discovery:
            return "Discovery"
        case .identity:
            return "Identity"
        case .calibration:
            return "Calibration"
        case .validation:
            return "Validation"
        case .completed:
            return "Completed"
        }
    }
    
    var description: String {
        switch self {
        case .discovery:
            return "Connect to robot network"
        case .identity:
            return "Configure robot identity"
        case .calibration:
            return "Calibrate robot systems"
        case .validation:
            return "Validate robot configuration"
        case .completed:
            return "Robot ready for operation"
        }
    }
}
