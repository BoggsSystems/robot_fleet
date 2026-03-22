import Foundation

protocol RobotServiceProtocol {
    func registerRobot(config: RobotConfig) async throws -> RobotRegistrationResponse
    func updateRobotOnboarding(robotId: String, request: OnboardingUpdateRequest) async throws -> OnboardingStatus
    func testRobotConnection(request: RobotConnectionTest) async throws -> RobotConnectionResponse
    func listRobots(fleetId: String?) async throws -> RobotListResponse
    func updateRobotStatus(robotId: String, update: RobotStatusUpdate) async throws -> RobotConfig
    func removeRobot(robotId: String) async throws -> Bool
    func calibrateRobot(request: CalibrationRequest) async throws -> CalibrationResponse
    func getRobot(robotId: String) async throws -> RobotConfig
}

class RobotServiceLive: RobotServiceProtocol {
    let apiClient: APIClientProtocol
    
    init(apiClient: APIClientProtocol = APIClient(baseURL: URL(string: "http://localhost:8000")!)) {
        self.apiClient = apiClient
    }
    
    func registerRobot(config: RobotConfig) async throws -> RobotRegistrationResponse {
        return try await apiClient.post(
            "api/robots/register",
            body: config,
            responseType: RobotRegistrationResponse.self
        )
    }
    
    func updateRobotOnboarding(robotId: String, request: OnboardingUpdateRequest) async throws -> OnboardingStatus {
        return try await apiClient.post(
            "api/backend/robots/\(robotId)/onboarding",
            body: request,
            responseType: OnboardingStatus.self
        )
    }
    
    func testRobotConnection(request: RobotConnectionTest) async throws -> RobotConnectionResponse {
        return try await apiClient.post(
            "api/robots/test-connection",
            body: request,
            responseType: RobotConnectionResponse.self
        )
    }
    
    func listRobots(fleetId: String? = nil) async throws -> RobotListResponse {
        let endpoint: String
        if let fleetId = fleetId {
            endpoint = "api/robots?fleet_id=\(fleetId)"
        } else {
            endpoint = "api/robots"
        }
        
        let response: [RobotConfig] = try await apiClient.get(endpoint, responseType: [RobotConfig].self)
        let availableRobots = response.filter { robot in
            RobotStatus(rawValue: robot.status)?.isAvailable ?? false
        }
        
        return RobotListResponse(
            robots: response,
            total: response.count,
            available: availableRobots.count
        )
    }
    
    func updateRobotStatus(robotId: String, update: RobotStatusUpdate) async throws -> RobotConfig {
        // Create a dictionary for the request body
        var requestBody: [String: Any] = [
            "status": update.status
        ]
        
        if let zoneId = update.zoneId {
            requestBody["zone_id"] = zoneId
        }
        
        if let capabilities = update.capabilities {
            requestBody["capabilities"] = capabilities
        }
        
        if let metadataUpdates = update.metadataUpdates {
            requestBody["metadata_updates"] = metadataUpdates
        }
        
        // Convert to JSON data for the request
        let jsonData = try JSONSerialization.data(withJSONObject: requestBody)
        let jsonString = String(data: jsonData, encoding: .utf8)!
        
        // Create a simple struct for the response
        struct RobotUpdateResponse: Codable {
            let robot: RobotConfig
        }
        
        return try await apiClient.post(
            "api/backend/robots/\(robotId)",
            body: jsonString,
            responseType: RobotUpdateResponse.self
        ).robot
    }
    
    func removeRobot(robotId: String) async throws -> Bool {
        struct DeleteResponse: Codable {
            let success: Bool
            let message: String
        }
        
        let response: DeleteResponse = try await apiClient.post(
            "api/backend/robots/\(robotId)",
            body: ["action": "delete"],
            responseType: DeleteResponse.self
        )
        
        return response.success
    }
    
    func calibrateRobot(request: CalibrationRequest) async throws -> CalibrationResponse {
        return try await apiClient.post(
            "api/robots/calibrate",
            body: request,
            responseType: CalibrationResponse.self
        )
    }
    
    func getRobot(robotId: String) async throws -> RobotConfig {
        struct RobotResponse: Codable {
            let robot: RobotConfig
        }
        
        let response: RobotResponse = try await apiClient.get(
            "api/robots/\(robotId)",
            responseType: RobotResponse.self
        )
        
        return response.robot
    }
}

// MARK: - Mock Service for Testing

class RobotServiceMock: RobotServiceProtocol {
    var mockRobots: [RobotConfig] = []
    var shouldFailRegistration = false
    var shouldFailConnection = false
    
    func registerRobot(config: RobotConfig) async throws -> RobotRegistrationResponse {
        if shouldFailRegistration {
            throw APIError.http(500)
        }
        
        var newRobot = config
        newRobot.status = RobotStatus.idle.rawValue
        
        mockRobots.append(newRobot)
        
        return RobotRegistrationResponse(
            success: true,
            message: "Robot \(config.name) registered successfully",
            robot: newRobot,
            onboarding: OnboardingStatus(
                robotId: config.robotId,
                stage: OnboardingStage.discovery.rawValue,
                status: "pending",
                details: [:],
                createdAt: ISO8601DateFormatter().string(from: Date()),
                updatedAt: ISO8601DateFormatter().string(from: Date())
            )
        )
    }
    
    func updateRobotOnboarding(robotId: String, request: OnboardingUpdateRequest) async throws -> OnboardingStatus {
        return OnboardingStatus(
            robotId: robotId,
            stage: request.stage,
            status: request.status,
            details: [:],
            createdAt: ISO8601DateFormatter().string(from: Date()),
            updatedAt: ISO8601DateFormatter().string(from: Date())
        )
    }
    
    func testRobotConnection(request: RobotConnectionTest) async throws -> RobotConnectionResponse {
        if shouldFailConnection {
            return RobotConnectionResponse(
                success: false,
                model: "",
                serial: "",
                firmware: "",
                battery: 0,
                message: "Connection failed"
            )
        }
        
        return RobotConnectionResponse(
            success: true,
            model: "Unitree R1",
            serial: "R1-2024-1234",
            firmware: "v2.1.4",
            battery: 87.0,
            message: "Connection successful"
        )
    }
    
    func listRobots(fleetId: String?) async throws -> RobotListResponse {
        let availableRobots = mockRobots.filter { robot in
            RobotStatus(rawValue: robot.status)?.isAvailable ?? false
        }
        
        return RobotListResponse(
            robots: mockRobots,
            total: mockRobots.count,
            available: availableRobots.count
        )
    }
    
    func updateRobotStatus(robotId: String, update: RobotStatusUpdate) async throws -> RobotConfig {
        guard let index = mockRobots.firstIndex(where: { $0.robotId == robotId }) else {
            throw APIError.invalidResponse
        }
        
        var updatedRobot = mockRobots[index]
        updatedRobot.status = update.status
        
        if let zoneId = update.zoneId {
            updatedRobot.zone = zoneId
        }
        
        if let capabilities = update.capabilities {
            updatedRobot.capabilities = capabilities
        }
        
        mockRobots[index] = updatedRobot
        return updatedRobot
    }
    
    func removeRobot(robotId: String) async throws -> Bool {
        mockRobots.removeAll { $0.robotId == robotId }
        return true
    }
    
    func calibrateRobot(request: CalibrationRequest) async throws -> CalibrationResponse {
        return CalibrationResponse(
            success: true,
            stage: "calibration",
            status: "completed",
            details: "Calibration completed successfully"
        )
    }
    
    func getRobot(robotId: String) async throws -> RobotConfig {
        guard let robot = mockRobots.first(where: { $0.robotId == robotId }) else {
            throw APIError.invalidResponse
        }
        return robot
    }
}
