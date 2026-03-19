import Foundation

protocol AuthServiceProtocol {
    func signIn(username: String, password: String, environment: AppEnvironment) async throws -> AuthSession
    func restoreSession(environment: AppEnvironment) async -> AuthSession?
    func signOut() async
}

enum AuthError: Error, LocalizedError {
    case invalidCredentials

    var errorDescription: String? {
        switch self {
        case .invalidCredentials:
            return "The username or password is incorrect."
        }
    }
}

final class AuthSessionStore {
    private let defaultsKey = "cottage.auth.session"

    func save(_ session: AuthSession) {
        guard let data = try? JSONEncoder().encode(session) else { return }
        UserDefaults.standard.set(data, forKey: defaultsKey)
    }

    func load() -> AuthSession? {
        guard
            let data = UserDefaults.standard.data(forKey: defaultsKey),
            let session = try? JSONDecoder().decode(AuthSession.self, from: data)
        else {
            return nil
        }
        return session
    }

    func clear() {
        UserDefaults.standard.removeObject(forKey: defaultsKey)
    }
}

final class AuthServiceLive: AuthServiceProtocol {
    private let sessionStore: AuthSessionStore

    init(sessionStore: AuthSessionStore) {
        self.sessionStore = sessionStore
    }

    func signIn(username: String, password: String, environment: AppEnvironment) async throws -> AuthSession {
        guard username == "admin", password == "demo123" else {
            throw AuthError.invalidCredentials
        }

        let session = AuthSession(
            userID: "local-admin",
            displayName: "Operations Admin",
            username: username,
            token: "local-demo-token",
            environment: environment.rawValue
        )
        sessionStore.save(session)
        return session
    }

    func restoreSession(environment: AppEnvironment) async -> AuthSession? {
        guard let session = sessionStore.load(), session.environment == environment.rawValue else {
            return nil
        }
        return session
    }

    func signOut() async {
        sessionStore.clear()
    }
}

struct AuthServiceMock: AuthServiceProtocol {
    func signIn(username: String, password: String, environment: AppEnvironment) async throws -> AuthSession {
        AuthSession(
            userID: "mock-admin",
            displayName: "Operations Admin",
            username: username,
            token: "mock-token",
            environment: environment.rawValue
        )
    }

    func restoreSession(environment: AppEnvironment) async -> AuthSession? {
        AuthSession(
            userID: "mock-admin",
            displayName: "Operations Admin",
            username: "admin",
            token: "mock-token",
            environment: environment.rawValue
        )
    }

    func signOut() async {}
}
