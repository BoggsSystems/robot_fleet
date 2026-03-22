import SwiftUI

struct RobotListView: View {
    @StateObject private var robotViewModel = RobotViewModel()
    @State private var showingAddRobot = false
    @State private var selectedFilter: RobotFilter = .all
    @State private var searchText = ""
    @State private var showingRobotDetail = false
    @State private var selectedRobot: RobotConfig?
    @State private var showingAlert = false
    @State private var alertMessage = ""
    
    enum RobotFilter: String, CaseIterable {
        case all = "All"
        case available = "Available"
        case busy = "Busy"
        case offline = "Offline"
        
        var status: RobotStatus? {
            switch self {
            case .all:
                return nil
            case .available:
                return .idle
            case .busy:
                return .busy
            case .offline:
                return .offline
            }
        }
    }
    
    var filteredRobots: [RobotConfig] {
        var robots = robotViewModel.robots
        
        // Apply status filter
        if let status = selectedFilter.status {
            robots = robots.filter { $0.robotStatus == status }
        }
        
        // Apply search filter
        if !searchText.isEmpty {
            robots = robots.filter { robot in
                robot.name.localizedCaseInsensitiveContains(searchText) ||
                robot.robotId.localizedCaseInsensitiveContains(searchText) ||
                robot.robotType.localizedCaseInsensitiveContains(searchText)
            }
        }
        
        return robots.sorted { $0.name < $1.name }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header with stats
                headerView
                
                // Search and filters
                searchAndFilterView
                
                // Robot list
                robotListView
            }
            .navigationTitle("Robot Fleet")
            .navigationBarTitleDisplayMode(.large)
            .toolbar {
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: { showingAddRobot = true }) {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showingAddRobot) {
                RobotRegistrationView(robotViewModel: robotViewModel)
            }
            .sheet(isPresented: $showingRobotDetail) {
                if let robot = selectedRobot {
                    RobotDetailView(robot: robot, robotViewModel: robotViewModel)
                }
            }
            .alert("Error", isPresented: $showingAlert) {
                Button("OK") { }
            } message: {
                Text(alertMessage)
            }
            .task {
                await robotViewModel.loadRobots()
            }
        }
    }
    
    private var headerView: some View {
        VStack(spacing: 16) {
            HStack {
                VStack(alignment: .leading, spacing: 4) {
                    Text("\(robotViewModel.robots.count)")
                        .font(.title)
                        .fontWeight(.bold)
                    Text("Total Robots")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text("\(robotViewModel.availableRobots.count)")
                        .font(.title2)
                        .fontWeight(.semibold)
                        .foregroundColor(.green)
                    Text("Available")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
            .padding()
            .background(Color(.systemGray6))
            .cornerRadius(12)
        }
        .padding(.horizontal)
        .padding(.top, 8)
    }
    
    private var searchAndFilterView: some View {
        VStack(spacing: 12) {
            // Search bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(.secondary)
                
                TextField("Search robots...", text: $searchText)
                    .textFieldStyle(PlainTextFieldStyle())
            }
            .padding(.horizontal, 12)
            .padding(.vertical, 8)
            .background(Color(.systemGray6))
            .cornerRadius(10)
            
            // Filter pills
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: 8) {
                    ForEach(RobotFilter.allCases, id: \.self) { filter in
                        Button(action: { selectedFilter = filter }) {
                            Text(filter.rawValue)
                                .font(.caption)
                                .fontWeight(.medium)
                                .padding(.horizontal, 12)
                                .padding(.vertical, 6)
                        }
                        .background(
                            selectedFilter == filter ? Color.blue : Color(.systemGray5),
                            in: RoundedRectangle(cornerRadius: 15)
                        )
                        .foregroundColor(
                            selectedFilter == filter ? .white : .primary
                        )
                    }
                }
                .padding(.horizontal)
            }
        }
        .padding(.horizontal)
        .padding(.vertical, 8)
    }
    
    private var robotListView: some View {
        Group {
            if filteredRobots.isEmpty {
                emptyStateView
            } else {
                List {
                    ForEach(filteredRobots) { robot in
                        RobotRowView(
                            robot: robot,
                            onTap: {
                                selectedRobot = robot
                                showingRobotDetail = true
                            }
                        )
                    }
                    .onDelete(perform: deleteRobots)
                }
                .listStyle(PlainListStyle())
            }
        }
    }
    
    private var emptyStateView: some View {
        VStack(spacing: 20) {
            Image(systemName: "robot")
                .font(.system(size: 60))
                .foregroundColor(.secondary)
            
            VStack(spacing: 8) {
                Text("No Robots Found")
                    .font(.title2)
                    .fontWeight(.semibold)
                
                Text(searchText.isEmpty ?
                     "Add your first robot to get started" :
                     "No robots match your search criteria")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .multilineTextAlignment(.center)
            }
            
            if searchText.isEmpty {
                Button("Add Robot") {
                    showingAddRobot = true
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .padding(40)
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }
    
    private func deleteRobots(at offsets: IndexSet) {
        Task {
            for index in offsets {
                let robot = filteredRobots[index]
                await robotViewModel.removeRobot(robotId: robot.robotId)
            }
        }
    }
}

struct RobotRowView: View {
    let robot: RobotConfig
    let onTap: () -> Void
    
    var body: some View {
        Button(action: onTap) {
            HStack(spacing: 12) {
                // Robot type icon
                Text(robot.robotTypeDisplay.icon)
                    .font(.title2)
                    .frame(width: 40, height: 40)
                    .background(robot.robotStatus.color.opacity(0.1))
                    .cornerRadius(8)
                
                // Robot info
                VStack(alignment: .leading, spacing: 4) {
                    HStack {
                        Text(robot.name)
                            .font(.headline)
                            .foregroundColor(.primary)
                        
                        Spacer()
                        
                        // Status badge
                        Text(robot.robotStatus.displayName)
                            .font(.caption)
                            .fontWeight(.medium)
                            .padding(.horizontal, 8)
                            .padding(.vertical, 4)
                            .background(robot.robotStatus.color.opacity(0.2))
                            .foregroundColor(robot.robotStatus.color)
                            .cornerRadius(6)
                    }
                    
                    HStack {
                        Text(robot.robotTypeDisplay.displayName)
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        // Battery indicator
                        if let battery = robot.batteryLevel {
                            HStack(spacing: 4) {
                                Image(systemName: "battery.\(Int(battery))")
                                    .foregroundColor(robot.batteryColor)
                                Text("\(Int(battery))%")
                                    .font(.caption)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    
                    // Location
                    HStack {
                        Image(systemName: "location")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        Text(robot.zone ?? "Unknown Location")
                            .font(.caption)
                            .foregroundColor(.secondary)
                        
                        Spacer()
                        
                        // Capabilities preview
                        Text(robot.capabilities.prefix(2).joined(separator: ", "))
                            .font(.caption2)
                            .foregroundColor(.secondary)
                            .lineLimit(1)
                    }
                }
                
                // Chevron
                Image(systemName: "chevron.right")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            .padding()
            .background(Color(.systemBackground))
            .cornerRadius(12)
        }
        .buttonStyle(PlainButtonStyle())
    }
}

// MARK: - Preview

struct RobotListView_Previews: PreviewProvider {
    static var previews: some View {
        RobotListView()
            .environmentObject(RobotViewModel(robotService: RobotServiceMock()))
    }
}
