import Foundation

// MARK: - Network Result

enum NetworkResult<T> {
    case success(T)
    case failure(NetworkError)
    case loading
}

// MARK: - Network Error

enum NetworkError: Error {
    case networkError(String)
    case serverError(Int, String)
    case unauthorizedError(String)
    case validationError(String)
    case timeoutError(String)
    case unknownError(String)
    
    var localizedDescription: String {
        switch self {
        case .networkError(let message):
            return message
        case .serverError(_, let message):
            return message
        case .unauthorizedError(let message):
            return message
        case .validationError(let message):
            return message
        case .timeoutError(let message):
            return message
        case .unknownError(let message):
            return message
        }
    }
    
    var isUnauthorized: Bool {
        if case .unauthorizedError = self {
            return true
        }
        return false
    }
}

// MARK: - Error Response Model

struct ErrorResponse: Codable {
    let error: String?
    let message: String?
    let detail: String?
    let statusCode: Int?
    
    enum CodingKeys: String, CodingKey {
        case error, message, detail
        case statusCode = "status_code"
    }
}
