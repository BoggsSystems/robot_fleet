import SwiftUI

struct MissionComposerView: View {
    @ObservedObject var viewModel: MissionComposerViewModel
    let onPreviewReady: (MissionPreviewResponse) -> Void

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("New Mission")
                .font(.largeTitle.bold())

            Text("Describe what you want done in natural language.")
                .foregroundStyle(.secondary)

            TextEditor(text: $viewModel.requestText)
                .frame(minHeight: 160)
                .padding(12)
                .overlay(RoundedRectangle(cornerRadius: 16).stroke(.quaternary))

            if let errorMessage = viewModel.errorMessage {
                Text(errorMessage)
                    .foregroundStyle(.red)
            }

            Button("Preview Mission") {
                Task { await viewModel.previewMission() }
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.requestText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || viewModel.isLoading)

            Spacer()
        }
        .padding(24)
        .onChange(of: viewModel.previewResponse) { _, preview in
            guard let preview else { return }
            onPreviewReady(preview)
        }
    }
}
