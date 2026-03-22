import SwiftUI

struct LoginView: View {
    @ObservedObject var session: AppSession
    @StateObject var viewModel: LoginViewModel

    var body: some View {
        VStack(alignment: .leading, spacing: 18) {
            Text("Cottage")
                .font(.largeTitle.bold())

            Text("Sign in to the operations terminal.")
                .foregroundStyle(.secondary)

            Picker("Environment", selection: $session.environment) {
                ForEach(AppEnvironment.allCases) { environment in
                    Text(environment.displayName).tag(environment)
                }
            }
            .pickerStyle(.segmented)

            VStack(alignment: .leading, spacing: 12) {
                TextField("Username", text: $viewModel.username)
                    .textFieldStyle(.roundedBorder)
                    .autocorrectionDisabled()

                SecureField("Password", text: $viewModel.password)
                    .textFieldStyle(.roundedBorder)
            }

            if let authError = session.authError {
                Text(authError)
                    .foregroundStyle(.red)
            }

            VStack(alignment: .leading, spacing: 4) {
                Text("Demo credentials")
                    .font(.caption.weight(.semibold))
                    .foregroundStyle(.secondary)
                Text("admin / demo123")
                    .font(.footnote.monospaced())
                    .foregroundStyle(.secondary)
            }

            Button("Sign In") {
                Task { await viewModel.signIn() }
            }
            .buttonStyle(.borderedProminent)
            .disabled(viewModel.username.isEmpty || viewModel.password.isEmpty || viewModel.isLoading)

            Spacer()
        }
        .padding(28)
        .frame(maxWidth: 420)
    }
}
