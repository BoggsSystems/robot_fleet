import SwiftUI

struct MissionPreviewView: View {
    @ObservedObject var viewModel: MissionPreviewViewModel
    let onMissionConfirmed: (MobileMission) -> Void

    var body: some View {
        let mission = viewModel.previewResponse.mission
        let detail = viewModel.detailResponse

        VStack(alignment: .leading, spacing: 14) {
            HStack {
                Text("Mission Approval")
                    .font(.title2.bold())
                Spacer()
                StatusBadge(status: mission.status)
            }

            Text(mission.title)
                .font(.headline)

            VStack(alignment: .leading, spacing: 10) {
                InfoRow(label: "From", value: mission.from ?? "Unspecified")
                InfoRow(label: "To", value: mission.to ?? "Unspecified")
                InfoRow(label: "Robot", value: mission.assignedRobotID ?? "To be assigned")
                InfoRow(label: "Summary", value: mission.summary)
            }
            .padding(14)
            .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))

            if let proposal = detail?.proposal {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Proposed Plan")
                        .font(.headline)

                    if let summary = proposal.plan?.summary {
                        Text(summary)
                            .font(.subheadline)
                    }

                    if !proposal.assumptions.isEmpty {
                        Text("Assumptions")
                            .font(.subheadline.weight(.semibold))
                        ForEach(proposal.assumptions, id: \.self) { item in
                            Text("• \(item)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }

                    if let notes = proposal.plan?.operatorNotes, !notes.isEmpty {
                        Text("Operator Notes")
                            .font(.subheadline.weight(.semibold))
                        ForEach(notes, id: \.self) { note in
                            Text("• \(note)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }

                    ForEach(proposal.plan?.candidateSteps ?? []) { step in
                        VStack(alignment: .leading, spacing: 6) {
                            Text(step.summary)
                                .font(.subheadline.weight(.semibold))
                            if let estimate = step.estimatedDurationMinutes {
                                Text("Estimated \(Int(estimate)) min")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                            if let firstCandidate = step.candidateAllocations.first {
                                Text("Top candidate: \(firstCandidate.displayName) (\(firstCandidate.robotType.capitalized))")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            } else {
                                Text("No current robot candidate")
                                    .font(.caption)
                                    .foregroundStyle(.orange)
                            }
                            if !step.routeLabels.isEmpty {
                                Text("Route: \(step.routeLabels.joined(separator: " -> "))")
                                    .font(.caption)
                                    .foregroundStyle(.secondary)
                            }
                        }
                        .padding(12)
                        .background(Color.gray.opacity(0.06), in: RoundedRectangle(cornerRadius: 12))
                    }
                }
                .padding(14)
                .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
            }

            if let validatedPlan = detail?.validatedPlan {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Validated Plan")
                        .font(.headline)
                    Text(validatedPlan.executable ? "Ready for approval and dispatch." : "Not executable yet.")
                        .font(.subheadline)
                        .foregroundStyle(validatedPlan.executable ? .green : .orange)

                    if !validatedPlan.blockingReasons.isEmpty {
                        Text("Blocking Reasons")
                            .font(.subheadline.weight(.semibold))
                        ForEach(validatedPlan.blockingReasons, id: \.self) { reason in
                            Text("• \(reason)")
                                .font(.caption)
                                .foregroundStyle(.orange)
                        }
                    }

                    if !validatedPlan.warnings.isEmpty {
                        Text("Warnings")
                            .font(.subheadline.weight(.semibold))
                        ForEach(validatedPlan.warnings, id: \.self) { warning in
                            Text("• \(warning)")
                                .font(.caption)
                                .foregroundStyle(.secondary)
                        }
                    }
                }
                .padding(14)
                .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
            }

            if let approval = detail?.approval {
                VStack(alignment: .leading, spacing: 8) {
                    Text("Approval")
                        .font(.headline)
                    InfoRow(label: "Required", value: approval.required ? "Yes" : "No")
                    InfoRow(label: "Status", value: approval.status.replacingOccurrences(of: "_", with: " ").capitalized)
                }
                .padding(14)
                .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
            }

            if let intent = viewModel.previewResponse.preview.intent {
                VStack(alignment: .leading, spacing: 10) {
                    Text("Planning Context")
                        .font(.headline)
                    InfoRow(label: "Priority", value: intent.priority.capitalized)
                    InfoRow(label: "Mission Type", value: intent.missionType.replacingOccurrences(of: "_", with: " ").capitalized)
                    InfoRow(label: "Capabilities", value: intent.requiredCapabilities.joined(separator: ", "))
                }
                .padding(14)
                .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 16))
            }

            if let errorMessage = viewModel.errorMessage {
                InlineErrorView(message: errorMessage)
            }

            Button("Approve Mission") {
                Task { await viewModel.approveMission() }
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.isConfirming || !(detail?.validatedPlan?.executable ?? true))
        }
        .padding(16)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
        .task { await viewModel.loadDetailIfNeeded() }
        .onChange(of: viewModel.confirmedMission) { _, mission in
            guard let mission else { return }
            onMissionConfirmed(mission)
        }
    }
}
