import Foundation

struct AuthSession: Codable, Equatable {
    let userID: String
    let displayName: String
    let username: String
    let token: String
    let environment: String
}

struct SignInRequest: Encodable, Equatable {
    let username: String
    let password: String
}

struct SignInResponse: Codable, Equatable {
    let session: AuthSession
}
