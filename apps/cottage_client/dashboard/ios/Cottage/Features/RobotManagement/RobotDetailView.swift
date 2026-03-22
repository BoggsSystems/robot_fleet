import SwiftUI

struct RobotDetailView: View {
    let robot: RobotConfig
    @ObservedObject var robotViewModel: RobotViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var showingCalibration = false
    @State private var showingEditSheet = false
    @State private var showingDeleteAlert = false
    @State private var calibrationError: String?
    
    var body: some View {
        NavigationView {
            ScrollView {
                VStack(spacing: 20) {
                    // Status header
                    statusHeaderView
                    
                    // Robot information
                    informationSection
                    
                    // Capabilities
                    capabilitiesSection
                    
                    // Location and network
                    locationSection
                    
                    // Actions
                    actionsSection
                }
                .padding()
            }
            .navigationTitle(robot.name)
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Menu {
                        Button("Edit") {
                            showingEditSheet = true
                        }
                        Button("Calibrate") {
                            showingCalibration = true
                        }
                        .disabled(robot.robotStatus != .idle)
                        
                        Divider()
                        
                        Button("Remove", role: .destructive) {
                            showingDeleteAlert = true
                        }
                    } label: {
                        Image(systemName: "ellipsis.circle")
                    }
                }
            }
            .sheet(isPresented: $showingEditSheet) {
                RobotEditView(robot: robot, robotViewModel: robotViewModel)
            }
            .alert("Calibration", isPresented: $showingCalibration) {
                Button("Cancel", role: .cancel) { }
                Button("Calibrate") {
                    Task {
                        await robotViewModel.calibrateRobot(robotId: robot.robotId)
                        if robotViewModel.error == nil {
                            showingCalibration = false
                        } else {
                            calibrationError = robotViewModel.error
                        }
                    }
                }
            } message: {
                Text("This will calibrate the robot's systems. The robot will be unavailable during calibration.")
            }
            .alert("Error", isPresented: Binding(
                get: { calibrationError != nil },
                set: { _ in calibrationError = nil }
            )) {
                Button("OK") { }
            } message: {
                Text(calibrationError ?? "")
            }
            .alert("Remove Robot", isPresented: $showingDeleteAlert) {
                Button("Cancel", role: .cancel) { }
                Button("Remove", role: .destructive) {
                    Task {
                        await robotViewModel.removeRobot(robotId: robot.robotId)
                        if robotViewModel.error == nil {
                            dismiss()
                        }
                    }
                }
            } message: {
                Text("Are you sure you want to remove \(robot.name)? This action cannot be undone.")
            }
        }
    }
    
    private var statusHeaderView: some View {
        VStack(spacing: 16) {
            HStack {
                // Robot icon and type
                VStack(spacing: 8) {
                    Text(robot.robotTypeDisplay.icon)
                        .font(.system(size: 50))
                    
                    Text(robot.robotTypeDisplay.displayName)
                        .font(.headline)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                // Status and battery
                VStack(alignment: .trailing, spacing: 12) {
                    // Status badge
                    VStack(spacing: 4) {
                        Text("Status")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Text(robot.robotStatus.displayName)
                            .font(.title2)
                            .fontWeight(.semibold)
                            .foregroundColor(robot.robotStatus.color)
                    }
                    
                    // Battery indicator
                    if let battery = robot.batteryLevel {
                        VStack(spacing: 4) {
                            Text("Battery")
                                .font(.caption)
                                .foregroundColor(.secondary)
                            
                            HStack(spacing: 8) {
                                Text("\(Int(battery))%")
                                    .font(.title2)
                                    .fontWeight(.semibold)
                                    .foregroundColor(robot.batteryColor)
                                
                                // Battery icon
                                Image(systemName: "battery.\(Int(battery))")
                                    .font(.title2)
                                    .foregroundColor(robot.batteryColor)
                            }
                        }
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemGray6))
        .cornerRadius(16)
    }
    
    private var informationSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Robot Information")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(alignment: .leading, spacing: 12) {
                InfoRow(title: "Robot ID", value: robot.robotId)
                InfoRow(title: "Display Name", value: robot.name)
                InfoRow(title: "Model", value: robot.model)
                InfoRow(title: "Vendor", value: robot.vendor)
                InfoRow(title: "Serial Number", value: robot.serial)
                InfoRow(title: "Firmware", value: robot.firmware)
                InfoRow(title: "Network Interface", value: robot.networkInterface)
                InfoRow(title: "IP Address", value: robot.ipAddress)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
    
    private var capabilitiesSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Capabilities")
                .font(.headline)
                .fontWeight(.semibold)
            
            if robot.capabilities.isEmpty {
                Text("No capabilities configured")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .italic()
            } else {
                LazyVGrid(columns: [
                    GridItem(.flexible()),
                    GridItem(.flexible())
                ], spacing: 8) {
                    ForEach(robot.capabilities, id: \.self) { capability in
                        Text(capability)
                            .font(.caption)
                            .fontWeight(.medium)
                            .padding(.horizontal, 12)
                            .padding(.vertical, 6)
                            .background(Color.blue.opacity(0.1))
                            .foregroundColor(.blue)
                            .cornerRadius(8)
                    }
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
    
    private var locationSection: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Location & Network")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(alignment: .leading, spacing: 12) {
                InfoRow(title: "Site", value: "Cottage")
                InfoRow(title: "Zone", value: robot.zone ?? "Not assigned")
                InfoRow(title: "Sub-zone", value: robot.subZone ?? "Not assigned")
                InfoRow(title: "Payload Capacity", value: robot.payloadCapacityKg != nil ? "\(robot.payloadCapacityKg!) kg" : "Not specified")
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
    
    private var actionsSection: some View {
        VStack(spacing: 12) {
            Text("Actions")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(spacing: 8) {
                // Test Connection
                Button(action: {
                    // Update registration config with current robot's IP and test
                    robotViewModel.updateRegistrationConfig([
                        "ipAddress": robot.ipAddress,
                        "networkInterface": robot.networkInterface
                    ])
                    Task {
                        await robotViewModel.testConnection()
                    }
                }) {
                    HStack {
                        Image(systemName: "network")
                        Text("Test Connection")
                    }
                }
                .buttonStyle(.bordered)
                
                // Calibrate
                Button(action: { showingCalibration = true }) {
                    HStack {
                        Image(systemName: "gear.badge.checkmark")
                        Text("Calibrate Robot")
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(robot.robotStatus != .idle)
                
                // Update Status
                Menu {
                    ForEach(RobotStatus.allCases, id: \.self) { status in
                        Button(status.displayName) {
                            Task {
                                await robotViewModel.updateRobotStatus(
                                    robotId: robot.robotId,
                                    update: RobotStatusUpdate(status: status.rawValue)
                                )
                            }
                        }
                        .disabled(status == robot.robotStatus)
                    }
                } label: {
                    HStack {
                        Image(systemName: "flag")
                        Text("Update Status")
                    }
                }
                .buttonStyle(.bordered)
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
    }
}

struct RobotEditView: View {
    let robot: RobotConfig
    @ObservedObject var robotViewModel: RobotViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var editedConfig: RobotConfig
    
    init(robot: RobotConfig, robotViewModel: RobotViewModel) {
        self.robot = robot
        self.robotViewModel = robotViewModel
        self._editedConfig = State(initialValue: robot)
    }
    
    var body: some View {
        NavigationView {
            Form {
                Section("Basic Information") {
                    TextField("Display Name", text: $editedConfig.name)
                    TextField("Model", text: $editedConfig.model)
                    TextField("Vendor", text: $editedConfig.vendor)
                    TextField("Serial Number", text: $editedConfig.serial)
                    TextField("Firmware Version", text: $editedConfig.firmware)
                }
                
                Section("Network Configuration") {
                    TextField("IP Address", text: $editedConfig.ipAddress)
                        .keyboardType(.numbersAndPunctuation)
                    TextField("Network Interface", text: $editedConfig.networkInterface)
                }
                
                Section("Location Assignment") {
                    TextField("Zone", text: Binding(
                        get: { editedConfig.zone ?? "" },
                        set: { editedConfig.zone = $0.isEmpty ? nil : $0 }
                    ))
                    TextField("Sub-zone", text: Binding(
                        get: { editedConfig.subZone ?? "" },
                        set: { editedConfig.subZone = $0.isEmpty ? nil : $0 }
                    ))
                }
                
                Section("Robot Type") {
                    Picker("Robot Type", selection: $editedConfig.robotType) {
                        ForEach(RobotType.allCases, id: \.rawValue) { type in
                            Text(type.displayName).tag(type.rawValue)
                        }
                    }
                    .pickerStyle(MenuPickerStyle())
                }
                
                Section("Payload Configuration") {
                    HStack {
                        Text("Payload Capacity")
                        Spacer()
                        TextField("kg", value: Binding(
                            get: { editedConfig.payloadCapacityKg ?? 0 },
                            set: { editedConfig.payloadCapacityKg = $0 }
                        ), format: .number)
                        .keyboardType(.decimalPad)
                        .frame(width: 80)
                    }
                }
            }
            .navigationTitle("Edit Robot")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        Task {
                            await robotViewModel.updateRobotStatus(
                                robotId: robot.robotId,
                                update: RobotStatusUpdate(
                                    status: editedConfig.status,
                                    zoneId: editedConfig.zone,
                                    capabilities: editedConfig.capabilities,
                                    metadataUpdates: editedConfig.metadata
                                )
                            )
                            if robotViewModel.error == nil {
                                dismiss()
                            }
                        }
                    }
                    .disabled(editedConfig == robot)
                }
            }
        }
    }
}

// MARK: - Preview

struct RobotDetailView_Previews: PreviewProvider {
    static var previews: some View {
        let mockRobot = RobotConfig(
            id: "1",
            robotId: "r1_warehouse_bot_01",
            name: "Carrier 01",
            ipAddress: "192.168.1.100",
            networkInterface: "eth0",
            capabilities: ["cargo_transport", "outdoor", "rough_terrain"],
            robotType: "quadruped",
            robotCategory: "quadruped",
            vendor: "Unitree",
            model: "Go2",
            serial: "R1-2024-1234",
            firmware: "v2.1.4",
            zone: "dock",
            subZone: "loading_area",
            status: "idle",
            batteryLevel: 87.0,
            payloadCapacityKg: 12.5,
            metadata: [:]
        )
        
        return RobotDetailView(
            robot: mockRobot,
            robotViewModel: RobotViewModel(robotService: RobotServiceMock())
        )
    }
}
