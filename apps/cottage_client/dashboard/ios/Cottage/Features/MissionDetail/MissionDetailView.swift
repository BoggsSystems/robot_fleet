import SwiftUI

struct MissionDetailView: View {
    @ObservedObject var viewModel: MissionDetailViewModel
    let onMissionUpdated: (MobileMission) -> Void

    var body: some View {
        Group {
            if let mission = viewModel.mission {
                ScrollView {
                    VStack(alignment: .leading, spacing: 18) {
                        HStack {
                            Text(mission.title)
                                .font(.largeTitle.bold())
                            Spacer()
                            StatusBadge(status: mission.status)
                        }

                        VStack(alignment: .leading, spacing: 10) {
                            InfoRow(label: "From", value: mission.from ?? "Unspecified")
                            InfoRow(label: "To", value: mission.to ?? "Unspecified")
                            InfoRow(label: "Assigned Robot", value: mission.assignedRobotID ?? "Unassigned")
                            InfoRow(label: "Approval", value: mission.approvalStatus.replacingOccurrences(of: "_", with: " ").capitalized)
                            InfoRow(label: "Task Count", value: "\(mission.taskCount)")
                            InfoRow(label: "Current Step", value: mission.currentStep ?? "Pending")
                            InfoRow(label: "Progress", value: "\(mission.completedSteps) / \(mission.totalSteps)")
                            InfoRow(label: "Fallback", value: mission.fallbackAvailable ? mission.fallbackRobotIDs.joined(separator: ", ") : "Unavailable")
                            InfoRow(label: "Replan", value: mission.replanAvailable ? "Available" : "None")
                            if let blockedReason = mission.blockedReason, !blockedReason.isEmpty {
                                InfoRow(label: "Blocked Reason", value: blockedReason)
                            }
                            InfoRow(label: "Summary", value: mission.summary)
                        }
                        .padding(14)
                        .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))

                        if let proposal = viewModel.proposal {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Proposed Plan")
                                    .font(.headline)
                                if let summary = proposal.plan?.summary {
                                    Text(summary)
                                        .font(.subheadline)
                                }
                                ForEach(proposal.assumptions, id: \.self) { assumption in
                                    Text("• \(assumption)")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                ForEach(proposal.plan?.operatorNotes ?? [], id: \.self) { note in
                                    Text("• \(note)")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                ForEach(proposal.warnings, id: \.self) { warning in
                                    Text("• \(warning)")
                                        .font(.caption)
                                        .foregroundStyle(.orange)
                                }
                            }
                            .padding(14)
                            .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
                        }

                        if let validatedPlan = viewModel.validatedPlan {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Validated Plan")
                                    .font(.headline)
                                Text(validatedPlan.executable ? "Executable" : "Blocked")
                                    .font(.subheadline)
                                    .foregroundStyle(validatedPlan.executable ? .green : .orange)
                                ForEach(validatedPlan.blockingReasons, id: \.self) { reason in
                                    Text("• \(reason)")
                                        .font(.caption)
                                        .foregroundStyle(.orange)
                                }
                            }
                            .padding(14)
                            .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
                        }

                        if let replan = viewModel.replan {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Replan Proposal")
                                    .font(.headline)
                                InfoRow(label: "Action", value: replan.action.replacingOccurrences(of: "_", with: " ").capitalized)
                                InfoRow(label: "Summary", value: replan.summary)
                                InfoRow(label: "Reason", value: replan.reason)
                                if let reviewSummary = replan.reviewSummary {
                                    InfoRow(label: "Review", value: reviewSummary)
                                }
                                if let provider = replan.provider {
                                    InfoRow(label: "Provider", value: provider)
                                }
                                if !replan.candidateRobotIDs.isEmpty {
                                    InfoRow(label: "Candidates", value: replan.candidateRobotIDs.joined(separator: ", "))
                                }
                                if !replan.routeLabels.isEmpty {
                                    InfoRow(label: "Route Override", value: replan.routeLabels.joined(separator: " -> "))
                                } else if !replan.routeNodes.isEmpty {
                                    InfoRow(label: "Route Override", value: replan.routeNodes.joined(separator: " -> "))
                                }
                                ForEach(replan.operatorNotes, id: \.self) { note in
                                    Text("• \(note)")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                                ForEach(replan.warnings, id: \.self) { warning in
                                    Text("• \(warning)")
                                        .font(.caption)
                                        .foregroundStyle(.orange)
                                }
                            }
                            .padding(14)
                            .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
                        }

                        if !viewModel.events.isEmpty {
                            VStack(alignment: .leading, spacing: 10) {
                                Text("Mission Activity")
                                    .font(.headline)
                                ForEach(viewModel.events) { event in
                                    VStack(alignment: .leading, spacing: 4) {
                                        HStack {
                                            Text(event.time)
                                                .font(.caption.monospacedDigit())
                                                .foregroundStyle(.secondary)
                                            Spacer()
                                            Text(event.status?.replacingOccurrences(of: "_", with: " ").capitalized ?? event.tone.capitalized)
                                                .font(.caption.weight(.semibold))
                                                .foregroundStyle(color(for: event.tone))
                                        }
                                        Text(event.message)
                                            .font(.subheadline)
                                    }
                                    .padding(12)
                                    .background(Color.gray.opacity(0.06), in: RoundedRectangle(cornerRadius: 12))
                                }
                            }
                        }

                        if mission.status != .completed && mission.status != .cancelled {
                            HStack {
                                if mission.status == .approved {
                                    Button("Dispatch Mission") {
                                        Task { await viewModel.dispatchMission() }
                                    }
                                    .buttonStyle(.borderedProminent)
                                }

                                if mission.status == .paused {
                                    Button("Resume Mission") {
                                        Task { await viewModel.resumeMission() }
                                    }
                                    .buttonStyle(.borderedProminent)
                                } else {
                                    Button("Pause Mission") {
                                        Task { await viewModel.pauseMission() }
                                    }
                                    .buttonStyle(.bordered)
                                }

                                if mission.status == .blocked {
                                    if viewModel.replan == nil {
                                        Button("Preview Replan") {
                                            Task { await viewModel.previewReplan() }
                                        }
                                        .buttonStyle(.bordered)
                                    } else {
                                        Button("Apply Replan") {
                                            Task { await viewModel.applyReplan() }
                                        }
                                        .buttonStyle(.borderedProminent)
                                    }

                                    Button("Retry Mission") {
                                        Task { await viewModel.retryMission() }
                                    }
                                    .buttonStyle(.borderedProminent)

                                    if mission.fallbackAvailable {
                                        Button("Use Fallback") {
                                            Task { await viewModel.useFallbackMission() }
                                        }
                                        .buttonStyle(.bordered)
                                    }
                                }

                                Button("Cancel Mission") {
                                    Task { await viewModel.cancelMission() }
                                }
                                .buttonStyle(.bordered)
                            }
                        }

                        Spacer()
                    }
                }
                .padding(24)
            } else if let errorMessage = viewModel.errorMessage {
                InlineErrorView(message: errorMessage)
            } else {
                VStack {
                    ProgressView()
                    Text("Loading mission details...")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }
            }
        }
        .task { await viewModel.load() }
        .onAppear { viewModel.startPolling() }
        .onDisappear { viewModel.stopPolling() }
        .onChange(of: viewModel.mission) { _, mission in
            guard let mission else { return }
            onMissionUpdated(mission)
        }
    }

    private func color(for tone: String) -> Color {
        switch tone {
        case "ok":
            return .green
        case "warn":
            return .orange
        default:
            return .blue
        }
    }
}
