import Foundation

@MainActor
final class LoginViewModel: ObservableObject {
    @Published var username = "admin"
    @Published var password = "demo123"
    @Published var isLoading = false

    private let session: AppSession

    init(session: AppSession) {
        self.session = session
    }

    func signIn() async {
        isLoading = true
        defer { isLoading = false }
        await session.signIn(username: username, password: password)
    }
}
