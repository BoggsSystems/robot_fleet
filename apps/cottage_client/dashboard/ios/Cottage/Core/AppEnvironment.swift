import Foundation

enum AppEnvironment: String, CaseIterable, Identifiable {
    case local
    case staging

    var id: String { rawValue }

    var displayName: String {
        switch self {
        case .local:
            return "Local"
        case .staging:
            return "Staging"
        }
    }

    var baseURL: URL {
        switch self {
        case .local:
            return URL(string: "http://127.0.0.1:8000")!
        case .staging:
            return URL(string: "https://staging.example.invalid")!
        }
    }
}
