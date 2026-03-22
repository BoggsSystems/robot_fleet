import Foundation

@MainActor
final class MissionDetailViewModel: ObservableObject {
    @Published var mission: MobileMission?
    @Published var events: [MissionEvent] = []
    @Published var proposal: MissionProposal?
    @Published var validatedPlan: ValidatedPlan?
    @Published var approval: ApprovalDecision?
    @Published var replan: ReplanProposal?
    @Published var isLoading = false
    @Published var errorMessage: String?

    let missionID: String
    private let missionService: MissionServiceProtocol
    private var pollingTask: Task<Void, Never>?

    init(missionID: String, missionService: MissionServiceProtocol) {
        self.missionID = missionID
        self.missionService = missionService
    }

    func load() async {
        errorMessage = nil
        isLoading = true
        defer { isLoading = false }

        do {
            let response = try await missionService.fetchMission(missionID: missionID)
            mission = response.mission
            events = response.events
            proposal = response.proposal
            validatedPlan = response.validatedPlan
            approval = response.approval
            replan = response.replan
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func startPolling() {
        pollingTask?.cancel()
        pollingTask = Task { [weak self] in
            while !Task.isCancelled {
                try? await Task.sleep(for: .seconds(3))
                guard let self, !Task.isCancelled else { return }
                await self.refreshSilently()
            }
        }
    }

    func stopPolling() {
        pollingTask?.cancel()
        pollingTask = nil
    }

    func cancelMission() async {
        errorMessage = nil
        do {
            mission = try await missionService.cancelMission(missionID: missionID)
            events = []
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func pauseMission() async {
        errorMessage = nil
        do {
            mission = try await missionService.pauseMission(missionID: missionID, requestedBy: "operator@local")
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func resumeMission() async {
        errorMessage = nil
        do {
            mission = try await missionService.resumeMission(missionID: missionID, requestedBy: "operator@local")
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func retryMission() async {
        errorMessage = nil
        do {
            mission = try await missionService.retryMission(missionID: missionID, requestedBy: "operator@local")
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func useFallbackMission() async {
        errorMessage = nil
        do {
            mission = try await missionService.useFallbackMission(missionID: missionID, requestedBy: "operator@local")
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func dispatchMission() async {
        errorMessage = nil
        do {
            let response = try await missionService.dispatchMission(missionID: missionID, confirmedBy: "operator@local")
            mission = response.mission
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func previewReplan() async {
        errorMessage = nil
        do {
            mission = try await missionService.previewReplan(missionID: missionID, requestedBy: "operator@local")
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func applyReplan() async {
        errorMessage = nil
        do {
            mission = try await missionService.applyReplan(missionID: missionID, requestedBy: "operator@local")
            await load()
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func refreshSilently() async {
        do {
            let response = try await missionService.fetchMission(missionID: missionID)
            mission = response.mission
            events = response.events
            proposal = response.proposal
            validatedPlan = response.validatedPlan
            approval = response.approval
            replan = response.replan
            errorMessage = nil
        } catch {
            // Keep the last good mission state on background refresh failures.
        }
    }

    deinit {
        pollingTask?.cancel()
    }
}
