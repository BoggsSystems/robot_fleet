import SwiftUI

struct RobotManagementTabView: View {
    @StateObject private var robotViewModel = RobotViewModel()
    @State private var selectedTab = 0
    
    private let tabs = ["Fleet", "Registration", "Status"]
    
    var body: some View {
        TabView(selection: $selectedTab) {
            // Fleet Overview Tab
            NavigationView {
                RobotListView()
            }
            .tabItem {
                Label("Fleet", systemImage: "list.bullet.rectangle")
            }
            .tag(0)
            
            // Registration Tab
            NavigationView {
                RobotRegistrationView(robotViewModel: robotViewModel)
            }
            .tabItem {
                Label("Add Robot", systemImage: "plus.circle")
            }
            .tag(1)
            
            // Status Dashboard Tab
            NavigationView {
                RobotStatusDashboardView(robotViewModel: robotViewModel)
            }
            .tabItem {
                Label("Status", systemImage: "chart.bar")
            }
            .tag(2)
        }
        .environmentObject(robotViewModel)
    }
}

struct RobotStatusDashboardView: View {
    @ObservedObject var robotViewModel: RobotViewModel
    
    var body: some View {
        ScrollView {
            VStack(spacing: 20) {
                // Summary cards
                summaryCardsView
                
                // Status breakdown
                statusBreakdownView
                
                // Type distribution
                typeDistributionView
                
                // Recent activity (placeholder)
                recentActivityView
            }
            .padding()
        }
        .navigationTitle("Fleet Status")
        .navigationBarTitleDisplayMode(.large)
        .task {
            await robotViewModel.loadRobots()
        }
    }
    
    private var summaryCardsView: some View {
        LazyVGrid(columns: [
            GridItem(.flexible()),
            GridItem(.flexible()),
            GridItem(.flexible())
            GridItem(.flexible())
        ], spacing: 16) {
            StatusCard(
                title: "Total Robots",
                value: "\(robotViewModel.robots.count)",
                color: .blue,
                icon: "robot"
            )
            
            StatusCard(
                title: "Available",
                value: "\(robotViewModel.availableRobots.count)",
                color: .green,
                icon: "checkmark.circle"
            )
            
            StatusCard(
                title: "Busy",
                value: "\(robotViewModel.busyRobots.count)",
                color: .orange,
                icon: "clock"
            )
            
            StatusCard(
                title: "Offline",
                value: "\(robotViewModel.offlineRobots.count)",
                color: .red,
                icon: "wifi.slash"
            )
        }
    }
    
    private var statusBreakdownView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Status Breakdown")
                .font(.headline)
                .fontWeight(.semibold)
            
            ForEach(Array(robotViewModel.robotsByStatus.keys.sorted(by: { $0.displayName < $1.displayName }), id: \.self) { status in
                if let robots = robotViewModel.robotsByStatus[status], !robots.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Circle()
                                .fill(status.color)
                                .frame(width: 12, height: 12)
                            
                            Text("\(status.displayName) (\(robots.count))")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            Spacer()
                        }
                        
                        // Robot list for this status
                        LazyVGrid(columns: [
                            GridItem(.flexible()),
                            GridItem(.flexible())
                        ], spacing: 8) {
                            ForEach(robots.prefix(4)) { robot in
                                VStack(spacing: 4) {
                                    Text(robot.robotTypeDisplay.icon)
                                        .font(.title2)
                                    
                                    Text(robot.name)
                                        .font(.caption)
                                        .lineLimit(1)
                                }
                                .padding(8)
                                .background(Color(.systemGray6))
                                .cornerRadius(8)
                            }
                        }
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                }
            }
        }
    }
    
    private var typeDistributionView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Robot Types")
                .font(.headline)
                .fontWeight(.semibold)
            
            ForEach(Array(robotViewModel.robotsByType.keys.sorted(by: { $0.displayName < $1.displayName }), id: \.self) { type in
                if let robots = robotViewModel.robotsByType[type], !robots.isEmpty {
                    VStack(alignment: .leading, spacing: 8) {
                        HStack {
                            Text(type.icon)
                                .font(.title2)
                            
                            Text("\(type.displayName) (\(robots.count))")
                                .font(.subheadline)
                                .fontWeight(.medium)
                            
                            Spacer()
                            
                            // Percentage
                            let percentage = Double(robots.count) / Double(robotViewModel.robots.count) * 100
                            Text("\(Int(percentage))%")
                                .font(.caption)
                                .foregroundColor(.secondary)
                        }
                        
                        // Progress bar
                        GeometryReader { geometry in
                            ZStack(alignment: .leading) {
                                Rectangle()
                                    .fill(Color(.systemGray5))
                                    .frame(height: 4)
                                
                                Rectangle()
                                    .fill(Color.blue)
                                    .frame(width: geometry.size.width * (percentage / 100), height: 4)
                            }
                        }
                        .frame(height: 4)
                    }
                    .padding()
                    .background(Color(.systemGray6))
                    .cornerRadius(12)
                }
            }
        }
    }
    
    private var recentActivityView: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Recent Activity")
                .font(.headline)
                .fontWeight(.semibold)
            
            VStack(spacing: 12) {
                HStack {
                    Image(systemName: "info.circle")
                        .foregroundColor(.blue)
                    
                    VStack(alignment: .leading, spacing: 4) {
                        Text("Fleet Status Updated")
                            .font(.subheadline)
                            .fontWeight(.medium)
                        Text("Real-time fleet monitoring active")
                            .font(.caption)
                            .foregroundColor(.secondary)
                    }
                    
                    Spacer()
                    
                    Text("Just now")
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
                .padding()
                .background(Color(.systemGray6))
                .cornerRadius(12)
                
                Text("Activity history will be available in future updates")
                    .font(.body)
                    .foregroundColor(.secondary)
                    .italic()
                    .frame(maxWidth: .infinity, alignment: .center)
                    .padding()
            }
        }
    }
}

struct StatusCard: View {
    let title: String
    let value: String
    let color: Color
    let icon: String
    
    var body: some View {
        VStack(spacing: 12) {
            HStack {
                Image(systemName: icon)
                    .font(.title2)
                    .foregroundColor(color)
                
                Spacer()
                
                VStack(alignment: .trailing, spacing: 4) {
                    Text(value)
                        .font(.title)
                        .fontWeight(.bold)
                    Text(title)
                        .font(.caption)
                        .foregroundColor(.secondary)
                }
            }
        }
        .padding()
        .background(Color(.systemBackground))
        .cornerRadius(12)
        .overlay(
            RoundedRectangle(cornerRadius: 12)
                .stroke(color.opacity(0.3), lineWidth: 1)
        )
    }
}

// MARK: - Preview

struct RobotManagementTabView_Previews: PreviewProvider {
    static var previews: some View {
        RobotManagementTabView()
            .environmentObject(RobotViewModel(robotService: RobotServiceMock()))
    }
}
