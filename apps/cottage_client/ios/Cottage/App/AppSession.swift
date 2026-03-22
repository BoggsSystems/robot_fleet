import Foundation

@MainActor
final class AppSession: ObservableObject {
    @Published private(set) var authSession: AuthSession?
    @Published var isRestoring = true
    @Published var authError: String?
    @Published var environment: AppEnvironment

    private let authService: AuthServiceProtocol

    init(environment: AppEnvironment, authService: AuthServiceProtocol) {
        self.environment = environment
        self.authService = authService
    }

    var isAuthenticated: Bool { authSession != nil }

    func restore() async {
        authSession = await authService.restoreSession(environment: environment)
        isRestoring = false
    }

    func signIn(username: String, password: String) async {
        authError = nil
        do {
            authSession = try await authService.signIn(username: username, password: password, environment: environment)
        } catch {
            authError = error.localizedDescription
        }
    }

    func signOut() async {
        await authService.signOut()
        authSession = nil
    }
}
