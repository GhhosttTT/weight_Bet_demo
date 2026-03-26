import Foundation

class BaseRepository {
    
    /// Safely execute API call and convert to NetworkResult
    func safeApiCall<T>(_ apiCall: @escaping (@escaping (Result<T, Error>) -> Void) -> Void) async -> NetworkResult<T> {
        return await withCheckedContinuation { continuation in
            apiCall { result in
                switch result {
                case .success(let data):
                    continuation.resume(returning: .success(data))
                case .failure(let error):
                    if let networkError = error as? NetworkError {
                        continuation.resume(returning: .failure(networkError))
                    } else if let urlError = error as? URLError {
                        let networkError = self.handleURLError(urlError)
                        continuation.resume(returning: .failure(networkError))
                    } else {
                        continuation.resume(returning: .failure(.unknownError(error.localizedDescription)))
                    }
                }
            }
        }
    }
    
    private func handleURLError(_ error: URLError) -> NetworkError {
        switch error.code {
        case .timedOut:
            return .timeoutError("Request timed out. Please check your network connection.")
        case .notConnectedToInternet, .networkConnectionLost:
            return .networkError("No internet connection. Please check your network settings.")
        case .cannotFindHost, .cannotConnectToHost:
            return .networkError("Cannot connect to server. Please try again later.")
        default:
            return .networkError(error.localizedDescription)
        }
    }
}
