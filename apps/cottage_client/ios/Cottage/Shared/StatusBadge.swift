import SwiftUI

struct StatusBadge: View {
    let status: MissionStatus

    var body: some View {
        Text(status.displayName)
            .font(.caption.weight(.semibold))
            .padding(.horizontal, 10)
            .padding(.vertical, 6)
            .background(backgroundColor.opacity(0.14))
            .foregroundStyle(backgroundColor)
            .clipShape(Capsule())
    }

    private var backgroundColor: Color {
        switch status {
        case .clarificationRequired:
            return .orange
        case .previewReady:
            return .blue
        case .planned, .dispatched, .inProgress:
            return .indigo
        case .completed:
            return .green
        case .blocked:
            return .red
        case .cancelled:
            return .gray
        }
    }
}
