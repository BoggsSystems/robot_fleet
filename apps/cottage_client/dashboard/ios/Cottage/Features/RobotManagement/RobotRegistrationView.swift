import SwiftUI

struct RobotRegistrationView: View {
    @ObservedObject var robotViewModel: RobotViewModel
    @Environment(\.dismiss) private var dismiss
    @State private var currentStep = 0
    @State private var showingConnectionTest = false
    
    private let steps = [
        "Discovery",
        "Identity", 
        "Configuration",
        "Validation"
    ]
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Progress indicator
                progressView
                
                // Step content
                stepContent
                
                Spacer()
                
                // Navigation buttons
                navigationButtons
            }
            .navigationTitle("Add Robot")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        dismiss()
                    }
                }
            }
            .alert("Connection Test", isPresented: $showingConnectionTest) {
                Button("OK") { }
            } message: {
                if let result = robotViewModel.connectionTestResult {
                    Text(result.message)
                }
            }
        }
    }
    
    private var progressView: some View {
        VStack(spacing: 8) {
            // Step indicators
            HStack {
                ForEach(0..<steps.count, id: \.self) { index in
                    VStack(spacing: 4) {
                        Circle()
                            .fill(index <= currentStep ? Color.blue : Color(.systemGray5))
                            .frame(width: 24, height: 24)
                            .overlay(
                                Text("\(index + 1)")
                                    .font(.caption)
                                    .fontWeight(.medium)
                                    .foregroundColor(index <= currentStep ? .white : .secondary)
                            )
                        
                        Text(steps[index])
                            .font(.caption)
                            .foregroundColor(index <= currentStep ? .blue : .secondary)
                    }
                    
                    if index < steps.count - 1 {
                        Rectangle()
                            .fill(index < currentStep ? Color.blue : Color(.systemGray5))
                            .frame(height: 2)
                    }
                }
            }
            
            // Current step title
            Text(steps[currentStep])
                .font(.title2)
                .fontWeight(.semibold)
                .padding(.top)
        }
        .padding()
        .background(Color(.systemGray6))
    }
    
    @ViewBuilder
    private var stepContent: some View {
        switch currentStep {
        case 0:
            DiscoveryStepView(
                config: $robotViewModel.registrationConfig,
                onUpdate: robotViewModel.updateRegistrationConfig,
                onTestConnection: {
                    Task {
                        await robotViewModel.testConnection()
                        showingConnectionTest = true
                    }
                },
                connectionResult: robotViewModel.connectionTestResult,
                isTesting: robotViewModel.isTestingConnection
            )
        case 1:
            IdentityStepView(
                config: $robotViewModel.registrationConfig,
                onUpdate: robotViewModel.updateRegistrationConfig
            )
        case 2:
            ConfigurationStepView(
                config: $robotViewModel.registrationConfig,
                onUpdate: robotViewModel.updateRegistrationConfig
            )
        case 3:
            ValidationStepView(
                config: robotViewModel.registrationConfig,
                onRegister: {
                    Task {
                        await robotViewModel.registerRobot()
                        if robotViewModel.error == nil {
                            dismiss()
                        }
                    }
                },
                isRegistering: robotViewModel.isRegistering,
                registrationError: robotViewModel.error
            )
        default:
            EmptyView()
        }
    }
    
    private var navigationButtons: some View {
        HStack(spacing: 16) {
            // Back button
            if currentStep > 0 {
                Button("Back") {
                    currentStep -= 1
                }
                .buttonStyle(.bordered)
            }
            
            Spacer()
            
            // Next/Register button
            if currentStep < steps.count - 1 {
                Button("Next") {
                    if canProceedToNext {
                        currentStep += 1
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!canProceedToNext)
            } else {
                Button("Register Robot") {
                    Task {
                        await robotViewModel.registerRobot()
                        if robotViewModel.error == nil {
                            dismiss()
                        }
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(!canRegister || robotViewModel.isRegistering)
                .overlay {
                    if robotViewModel.isRegistering {
                        ProgressView()
                            .scaleEffect(0.8)
                    }
                }
            }
        }
        .padding()
    }
    
    private var canProceedToNext: Bool {
        switch currentStep {
        case 0:
            return !robotViewModel.registrationConfig.ipAddress.isEmpty &&
                   robotViewModel.connectionTestResult?.success == true
        case 1:
            return !robotViewModel.registrationConfig.robotId.isEmpty &&
                   !robotViewModel.registrationConfig.name.isEmpty
        case 2:
            return true
        default:
            return false
        }
    }
    
    private var canRegister: Bool {
        return !robotViewModel.registrationConfig.robotId.isEmpty &&
               !robotViewModel.registrationConfig.name.isEmpty &&
               !robotViewModel.registrationConfig.ipAddress.isEmpty &&
               robotViewModel.connectionTestResult?.success == true
    }
}

// MARK: - Step Views

struct DiscoveryStepView: View {
    @Binding var config: RobotConfig
    let onUpdate: (Partial<RobotConfig>) -> Void
    let onTestConnection: () -> Void
    let connectionResult: RobotConnectionResponse?
    let isTesting: Bool
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Connect to Robot")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Enter the robot's network information to establish a connection.")
                .font(.body)
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 16) {
                // IP Address
                VStack(alignment: .leading, spacing: 8) {
                    Text("IP Address")
                        .font(.headline)
                    
                    TextField("192.168.1.100", text: Binding(
                        get: { config.ipAddress },
                        set: { onUpdate(["ipAddress": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .keyboardType(.numbersAndPunctuation)
                }
                
                // Network Interface
                VStack(alignment: .leading, spacing: 8) {
                    Text("Network Interface")
                        .font(.headline)
                    
                    TextField("eth0", text: Binding(
                        get: { config.networkInterface },
                        set: { onUpdate(["networkInterface": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Connection Test
                Button(action: onTestConnection) {
                    HStack {
                        if isTesting {
                            ProgressView()
                                .scaleEffect(0.8)
                        } else {
                            Image(systemName: "network")
                        }
                        Text(isTesting ? "Testing..." : "Test Connection")
                    }
                }
                .buttonStyle(.borderedProminent)
                .disabled(config.ipAddress.isEmpty || isTesting)
                
                // Connection Result
                if let result = connectionResult {
                    HStack {
                        Image(systemName: result.success ? "checkmark.circle.fill" : "xmark.circle.fill")
                            .foregroundColor(result.success ? .green : .red)
                        
                        VStack(alignment: .leading, spacing: 4) {
                            Text(result.success ? "Connection Successful" : "Connection Failed")
                                .fontWeight(.medium)
                            Text(result.message)
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                    }
                    .padding()
                    .background(result.success ? Color.green.opacity(0.1) : Color.red.opacity(0.1))
                    .cornerRadius(8)
                }
            }
            
            Spacer()
        }
        .padding()
    }
}

struct IdentityStepView: View {
    @Binding var config: RobotConfig
    let onUpdate: (Partial<RobotConfig>) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Robot Identity")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Configure the robot's identification and classification.")
                .font(.body)
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 16) {
                // Robot ID
                VStack(alignment: .leading, spacing: 8) {
                    Text("Robot ID")
                        .font(.headline)
                    
                    TextField("r1_warehouse_bot_01", text: Binding(
                        get: { config.robotId },
                        set: { onUpdate(["robotId": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                    .autocapitalization(.none)
                    .disableAutocorrection(true)
                }
                
                // Display Name
                VStack(alignment: .leading, spacing: 8) {
                    Text("Display Name")
                        .font(.headline)
                    
                    TextField("Carrier 01", text: Binding(
                        get: { config.name },
                        set: { onUpdate(["name": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Robot Type
                VStack(alignment: .leading, spacing: 8) {
                    Text("Robot Type")
                        .font(.headline)
                    
                    Picker("Robot Type", selection: Binding(
                        get: { config.robotType },
                        set: { onUpdate(["robotType": $0]) }
                    )) {
                        ForEach(RobotType.allCases, id: \.rawValue) { type in
                            Text(type.displayName).tag(type.rawValue)
                        }
                    }
                    .pickerStyle(MenuPickerStyle())
                }
                
                // Vendor
                VStack(alignment: .leading, spacing: 8) {
                    Text("Vendor")
                        .font(.headline)
                    
                    TextField("Unitree", text: Binding(
                        get: { config.vendor },
                        set: { onUpdate(["vendor": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
            }
            
            Spacer()
        }
        .padding()
    }
}

struct ConfigurationStepView: View {
    @Binding var config: RobotConfig
    let onUpdate: (Partial<RobotConfig>) -> Void
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Configuration")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Set up the robot's operational parameters and capabilities.")
                .font(.body)
                .foregroundColor(.secondary)
            
            VStack(alignment: .leading, spacing: 16) {
                // Model
                VStack(alignment: .leading, spacing: 8) {
                    Text("Model")
                        .font(.headline)
                    
                    TextField("Go2", text: Binding(
                        get: { config.model },
                        set: { onUpdate(["model": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Serial Number
                VStack(alignment: .leading, spacing: 8) {
                    Text("Serial Number")
                        .font(.headline)
                    
                    TextField("R1-2024-1234", text: Binding(
                        get: { config.serial },
                        set: { onUpdate(["serial": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Firmware Version
                VStack(alignment: .leading, spacing: 8) {
                    Text("Firmware Version")
                        .font(.headline)
                    
                    TextField("v2.1.4", text: Binding(
                        get: { config.firmware },
                        set: { onUpdate(["firmware": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Zone Assignment
                VStack(alignment: .leading, spacing: 8) {
                    Text("Work Zone")
                        .font(.headline)
                    
                    TextField("dock", text: Binding(
                        get: { config.zone ?? "" },
                        set: { onUpdate(["zone": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
                
                // Sub-zone
                VStack(alignment: .leading, spacing: 8) {
                    Text("Sub-zone")
                        .font(.headline)
                    
                    TextField("loading_area", text: Binding(
                        get: { config.subZone ?? "" },
                        set: { onUpdate(["subZone": $0]) }
                    ))
                    .textFieldStyle(RoundedBorderTextFieldStyle())
                }
            }
            
            Spacer()
        }
        .padding()
    }
}

struct ValidationStepView: View {
    let config: RobotConfig
    let onRegister: () -> Void
    let isRegistering: Bool
    let registrationError: String?
    
    var body: some View {
        VStack(alignment: .leading, spacing: 20) {
            Text("Validation")
                .font(.title2)
                .fontWeight(.semibold)
            
            Text("Review the robot configuration before registering.")
                .font(.body)
                .foregroundColor(.secondary)
            
            // Configuration summary
            VStack(alignment: .leading, spacing: 12) {
                Text("Configuration Summary")
                    .font(.headline)
                
                VStack(alignment: .leading, spacing: 8) {
                    InfoRow(title: "Robot ID", value: config.robotId)
                    InfoRow(title: "Name", value: config.name)
                    InfoRow(title: "Type", value: RobotType(rawValue: config.robotType)?.displayName ?? config.robotType)
                    InfoRow(title: "IP Address", value: config.ipAddress)
                    InfoRow(title: "Network Interface", value: config.networkInterface)
                    InfoRow(title: "Model", value: config.model)
                    InfoRow(title: "Vendor", value: config.vendor)
                    InfoRow(title: "Zone", value: config.zone ?? "Not assigned")
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
            
            // Error display
            if let error = registrationError {
                VStack(alignment: .leading, spacing: 8) {
                    HStack {
                        Image(systemName: "exclamationmark.triangle.fill")
                            .foregroundColor(.red)
                        Text("Registration Error")
                            .font(.headline)
                            .foregroundColor(.red)
                    }
                    
                    Text(error)
                        .font(.body)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color.red.opacity(0.1))
                .cornerRadius(12)
            }
            
            Spacer()
        }
        .padding()
    }
}

// MARK: - Custom Text Field Style

struct RoundedBorderTextFieldStyle: TextFieldStyle {
    func _body(configuration: TextField<Self._Label>) -> some View {
        configuration
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.systemBackground))
            .overlay(
                RoundedRectangle(cornerRadius: 8)
                    .stroke(Color(.systemGray4), lineWidth: 1)
            )
            .cornerRadius(8)
    }
}

// MARK: - Preview

struct RobotRegistrationView_Previews: PreviewProvider {
    static var previews: some View {
        RobotRegistrationView(robotViewModel: RobotViewModel(robotService: RobotServiceMock()))
    }
}
