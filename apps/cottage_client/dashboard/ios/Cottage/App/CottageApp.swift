import SwiftUI

@main
struct CottageApp: App {
    private let container = AppContainer.live(environment: .local)
    @StateObject private var session: AppSession

    init() {
        let container = AppContainer.live(environment: .local)
        self.container = container
        _session = StateObject(
            wrappedValue: AppSession(environment: container.environment, authService: container.authService)
        )
    }

    var body: some Scene {
        WindowGroup {
            Group {
                if session.isRestoring {
                    ProgressView()
                } else if session.isAuthenticated {
                    EnhancedRootView(container: container, session: session)
                } else {
                    LoginView(session: session, viewModel: LoginViewModel(session: session))
                }
            }
            .task {
                if session.isRestoring {
                    await session.restore()
                }
            }
        }
    }
}
