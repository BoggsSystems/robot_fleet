import Foundation

enum APIError: Error, LocalizedError {
    case invalidResponse
    case http(Int)
    case decodingFailed

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The server response was invalid."
        case .http(let code):
            return "The server returned HTTP \(code)."
        case .decodingFailed:
            return "The response could not be decoded."
        }
    }
}

protocol APIClientProtocol {
    func get<T: Decodable>(_ path: String, responseType: T.Type) async throws -> T
    func post<Body: Encodable, T: Decodable>(_ path: String, body: Body, responseType: T.Type) async throws -> T
}

struct APIClient: APIClientProtocol {
    let baseURL: URL
    let session: URLSession = .shared

    func get<T: Decodable>(_ path: String, responseType: T.Type) async throws -> T {
        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = "GET"
        return try await perform(request, responseType: responseType)
    }

    func post<Body: Encodable, T: Decodable>(_ path: String, body: Body, responseType: T.Type) async throws -> T {
        var request = URLRequest(url: baseURL.appendingPathComponent(path))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(body)
        return try await perform(request, responseType: responseType)
    }

    private func perform<T: Decodable>(_ request: URLRequest, responseType: T.Type) async throws -> T {
        let (data, response) = try await session.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        guard (200 ..< 300).contains(http.statusCode) else {
            throw APIError.http(http.statusCode)
        }
        do {
            let decoder = JSONDecoder()
            return try decoder.decode(T.self, from: data)
        } catch {
            throw APIError.decodingFailed
        }
    }
}
