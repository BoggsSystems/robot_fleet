import Foundation
import SwiftUI

@MainActor
class RobotViewModel: ObservableObject {
    @Published var robots: [RobotConfig] = []
    @Published var isLoading = false
    @Published var error: String?
    @Published var selectedRobot: RobotConfig?
    @Published var registrationConfig = RobotConfig.empty
    @Published var connectionTestResult: RobotConnectionResponse?
    @Published var isRegistering = false
    @Published var isTestingConnection = false
    @Published var onboardingStatus: OnboardingStatus?
    
    private let robotService: RobotServiceProtocol
    
    init(robotService: RobotServiceProtocol = RobotServiceLive()) {
        self.robotService = robotService
    }
    
    // MARK: - Robot Management
    
    func loadRobots(fleetId: String? = nil) async {
        await MainActor.run {
            isLoading = true
            error = nil
        }
        
        do {
            let response = try await robotService.listRobots(fleetId: fleetId)
            await MainActor.run {
                self.robots = response.robots.sorted { $0.name < $1.name }
                isLoading = false
            }
        } catch {
            await MainActor.run {
                self.error = "Failed to load robots: \(error.localizedDescription)"
                isLoading = false
            }
        }
    }
    
    func registerRobot() async {
        await MainActor.run {
            isRegistering = true
            error = nil
        }
        
        do {
            let response = try await robotService.registerRobot(config: registrationConfig)
            await MainActor.run {
                self.robots.append(response.robot)
                self.registrationConfig = RobotConfig.empty
                self.isRegistering = false
                self.onboardingStatus = response.onboarding
            }
        } catch {
            await MainActor.run {
                self.error = "Failed to register robot: \(error.localizedDescription)"
                self.isRegistering = false
            }
        }
    }
    
    func updateRobotStatus(robotId: String, update: RobotStatusUpdate) async {
        do {
            let updatedRobot = try await robotService.updateRobotStatus(robotId: robotId, update: update)
            await MainActor.run {
                if let index = robots.firstIndex(where: { $0.robotId == robotId }) {
                    robots[index] = updatedRobot
                }
            }
        } catch {
            await MainActor.run {
                self.error = "Failed to update robot status: \(error.localizedDescription)"
            }
        }
    }
    
    func removeRobot(robotId: String) async {
        guard let robot = robots.first(where: { $0.robotId == robotId }) else { return }
        
        let confirmationMessage = "Are you sure you want to remove \(robot.name)? This action cannot be undone."
        
        // In a real app, you'd show an alert here
        // For now, proceed with removal
        
        do {
            let success = try await robotService.removeRobot(robotId: robotId)
            if success {
                await MainActor.run {
                    robots.removeAll { $0.robotId == robotId }
                    if selectedRobot?.robotId == robotId {
                        selectedRobot = nil
                    }
                }
            }
        } catch {
            await MainActor.run {
                self.error = "Failed to remove robot: \(error.localizedDescription)"
            }
        }
    }
    
    // MARK: - Connection Testing
    
    func testConnection() async {
        await MainActor.run {
            isTestingConnection = true
            connectionTestResult = nil
            error = nil
        }
        
        let testRequest = RobotConnectionTest(
            ipAddress: registrationConfig.ipAddress,
            networkInterface: registrationConfig.networkInterface
        )
        
        do {
            let response = try await robotService.testRobotConnection(request: testRequest)
            await MainActor.run {
                self.connectionTestResult = response
                self.isTestingConnection = false
            }
        } catch {
            await MainActor.run {
                self.error = "Connection test failed: \(error.localizedDescription)"
                self.isTestingConnection = false
            }
        }
    }
    
    // MARK: - Onboarding
    
    func updateOnboarding(robotId: String, stage: OnboardingStage, status: String, details: String = "") async {
        let request = OnboardingUpdateRequest(
            stage: stage.rawValue,
            status: status,
            details: details
        )
        
        do {
            let response = try await robotService.updateRobotOnboarding(robotId: robotId, request: request)
            await MainActor.run {
                self.onboardingStatus = response
            }
        } catch {
            await MainActor.run {
                self.error = "Failed to update onboarding: \(error.localizedDescription)"
            }
        }
    }
    
    func calibrateRobot(robotId: String, calibrationType: String = "full") async {
        let request = CalibrationRequest(
            robotId: robotId,
            calibrationType: calibrationType
        )
        
        do {
            let response = try await robotService.calibrateRobot(request: request)
            await MainActor.run {
                if response.success {
                    // Update robot status to reflect calibration
                    updateRobotStatus(robotId: robotId, update: RobotStatusUpdate(
                        status: RobotStatus.calibration.rawValue
                    ))
                }
            }
        } catch {
            await MainActor.run {
                self.error = "Calibration failed: \(error.localizedDescription)"
            }
        }
    }
    
    // MARK: - Selection
    
    func selectRobot(_ robot: RobotConfig) {
        selectedRobot = robot
    }
    
    func clearSelection() {
        selectedRobot = nil
    }
    
    // MARK: - Configuration Helpers
    
    func updateRegistrationConfig(_ updates: Partial<RobotConfig>) {
        registrationConfig = registrationConfig.with(updates)
    }
    
    func resetRegistrationConfig() {
        registrationConfig = RobotConfig.empty
    }
    
    // MARK: - Computed Properties
    
    var availableRobots: [RobotConfig] {
        robots.filter { robot in
            RobotStatus(rawValue: robot.status)?.isAvailable ?? false
        }
    }
    
    var busyRobots: [RobotConfig] {
        robots.filter { robot in
            RobotStatus(rawValue: robot.status) == .busy
        }
    }
    
    var offlineRobots: [RobotConfig] {
        robots.filter { robot in
            RobotStatus(rawValue: robot.status) == .offline
        }
    }
    
    var robotsByType: [RobotType: [RobotConfig]] {
        Dictionary(grouping: robots) { robot in
            RobotType(rawValue: robot.robotType) ?? .unknown
        }
    }
    
    var robotsByStatus: [RobotStatus: [RobotConfig]] {
        Dictionary(grouping: robots) { robot in
            RobotStatus(rawValue: robot.status) ?? .offline
        }
    }
}

// MARK: - Robot Config Extension

extension RobotConfig {
    static let empty = RobotConfig(
        id: UUID().uuidString,
        robotId: "",
        name: "",
        ipAddress: "",
        networkInterface: "",
        capabilities: [],
        robotType: RobotType.quadruped.rawValue,
        robotCategory: "quadruped",
        vendor: "Unitree",
        model: "Go2",
        serial: "",
        firmware: "",
        zone: nil,
        subZone: nil,
        status: RobotStatus.offline.rawValue,
        batteryLevel: nil,
        payloadCapacityKg: nil,
        metadata: [:]
    )
    
    func with(_ updates: Partial<RobotConfig>) -> RobotConfig {
        var new = self
        if let id = updates.id { new.id = id }
        if let robotId = updates.robotId { new.robotId = robotId }
        if let name = updates.name { new.name = name }
        if let ipAddress = updates.ipAddress { new.ipAddress = ipAddress }
        if let networkInterface = updates.networkInterface { new.networkInterface = networkInterface }
        if let capabilities = updates.capabilities { new.capabilities = capabilities }
        if let robotType = updates.robotType { new.robotType = robotType }
        if let robotCategory = updates.robotCategory { new.robotCategory = robotCategory }
        if let vendor = updates.vendor { new.vendor = vendor }
        if let model = updates.model { new.model = model }
        if let serial = updates.serial { new.serial = serial }
        if let firmware = updates.firmware { new.firmware = firmware }
        if let zone = updates.zone { new.zone = zone }
        if let subZone = updates.subZone { new.subZone = subZone }
        if let status = updates.status { new.status = status }
        if let batteryLevel = updates.batteryLevel { new.batteryLevel = batteryLevel }
        if let payloadCapacityKg = updates.payloadCapacityKg { new.payloadCapacityKg = payloadCapacityKg }
        if let metadata = updates.metadata { new.metadata = metadata }
        return new
    }
    
    var robotStatus: RobotStatus {
        RobotStatus(rawValue: status) ?? .offline
    }
    
    var robotTypeDisplay: RobotType {
        RobotType(rawValue: robotType) ?? .unknown
    }
    
    var isAvailable: Bool {
        robotStatus.isAvailable
    }
    
    var batteryPercentage: Float {
        batteryLevel ?? 0.0
    }
    
    var batteryColor: Color {
        switch batteryPercentage {
        case 0...20:
            return .red
        case 21...50:
            return .orange
        case 51...80:
            return .yellow
        default:
            return .green
        }
    }
    
    var capabilitiesDisplay: String {
        capabilities.isEmpty ? "None" : capabilities.joined(separator: ", ")
    }
}

// MARK: - Dictionary Helper

extension Dictionary {
    init(grouping values: [RobotConfig], by keyPath: KeyPath<RobotConfig, RobotType>) {
        self = { [RobotType: [RobotConfig]]() }()
        for value in values {
            let key = value[keyPath: keyPath]
            self[key, default: []].append(value)
        }
    }
    
    init(grouping values: [RobotConfig], by keyPath: KeyPath<RobotConfig, RobotStatus>) {
        self = { [RobotStatus: [RobotConfig]]() }()
        for value in values {
            let key = value[keyPath: keyPath]
            self[key, default: []].append(value)
        }
    }
}
