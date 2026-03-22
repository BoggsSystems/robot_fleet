import SwiftUI

struct MissionClarificationView: View {
    @ObservedObject var viewModel: MissionClarificationViewModel
    let onPreviewResolved: (MissionPreviewResponse) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Clarification")
                .font(.title2.bold())

            Text(viewModel.mission.clarificationQuestion?.prompt ?? "Please clarify the mission.")
                .foregroundStyle(.secondary)

            TextField("Answer", text: $viewModel.answer)
                .textFieldStyle(.roundedBorder)

            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }

            Button("Submit") {
                Task { await viewModel.submitClarification() }
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.answer.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || viewModel.isLoading)
        }
        .padding(16)
        .background(.thinMaterial, in: RoundedRectangle(cornerRadius: 18))
        .onChange(of: viewModel.updatedPreview) { _, preview in
            guard let preview else { return }
            onPreviewResolved(preview)
        }
    }
}
