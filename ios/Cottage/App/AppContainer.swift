import Foundation

struct AppContainer {
    let environment: AppEnvironment
    let authService: AuthServiceProtocol
    let missionService: MissionServiceProtocol

    static func live(environment: AppEnvironment) -> AppContainer {
        let client = APIClient(baseURL: environment.baseURL)
        let sessionStore = AuthSessionStore()
        return AppContainer(
            environment: environment,
            authService: AuthServiceLive(sessionStore: sessionStore),
            missionService: MissionServiceLive(apiClient: client)
        )
    }

    static func mock(environment: AppEnvironment = .local) -> AppContainer {
        AppContainer(
            environment: environment,
            authService: AuthServiceMock(),
            missionService: MissionServiceMock()
        )
    }
}
