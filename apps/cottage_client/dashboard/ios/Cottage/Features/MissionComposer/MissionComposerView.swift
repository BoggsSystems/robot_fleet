import SwiftUI

struct MissionComposerView: View {
    @ObservedObject var viewModel: MissionComposerViewModel
    let onPreviewReady: (MissionPreviewResponse) -> Void
    private let quickPrompts = [
        "Bring groceries from dock to kitchen",
        "Inspect the dock",
        "Move supplies from landing to entry",
    ]

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 20) {
                VStack(alignment: .leading, spacing: 8) {
                    Text("New Mission")
                        .font(.largeTitle.bold())

                    Text("Describe the job in plain language. The backend will interpret it, validate it, and prepare a mission preview before anything runs.")
                        .foregroundStyle(.secondary)
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Quick Start")
                        .font(.headline)

                    ForEach(quickPrompts, id: \.self) { prompt in
                        Button {
                            viewModel.requestText = prompt
                        } label: {
                            HStack {
                                Image(systemName: "sparkles")
                                    .foregroundStyle(.indigo)
                                Text(prompt)
                                    .foregroundStyle(.primary)
                                Spacer()
                            }
                            .padding(12)
                            .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 14))
                        }
                        .buttonStyle(.plain)
                    }
                }

                VStack(alignment: .leading, spacing: 10) {
                    Text("Mission Request")
                        .font(.headline)

                    TextEditor(text: $viewModel.requestText)
                        .frame(minHeight: 180)
                        .padding(12)
                        .background(Color.gray.opacity(0.08), in: RoundedRectangle(cornerRadius: 18))

                    Text("Example: “Bring groceries from dock to kitchen.”")
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                }

                if let errorMessage = viewModel.errorMessage {
                    InlineErrorView(message: errorMessage)
                }

                Button {
                    Task { await viewModel.previewMission() }
                } label: {
                    HStack {
                        if viewModel.isLoading {
                            ProgressView()
                                .tint(.white)
                        }
                        Text(viewModel.isLoading ? "Preparing Preview..." : "Preview Mission")
                    }
                    .frame(maxWidth: .infinity)
                }
                .buttonStyle(.borderedProminent)
                .disabled(viewModel.requestText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty || viewModel.isLoading)
            }
        }
        .padding(24)
        .onChange(of: viewModel.previewResponse) { _, preview in
            guard let preview else { return }
            onPreviewReady(preview)
        }
    }
}
