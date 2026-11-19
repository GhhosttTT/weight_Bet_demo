import Foundation
import Alamofire

final class AuthInterceptor: RequestInterceptor {
    private let keychainManager = KeychainManager.shared
    private lazy var authRepository = AuthRepository.shared // 懒加载，打破循环依赖
    private let refreshLock = NSLock()
    private var refreshInFlight = false
    private var refreshCompletions: [(Result<AuthResponse, Error>) -> Void] = []
    
    func adapt(_ urlRequest: URLRequest, for session: Session, completion: @escaping (Result<URLRequest, Error>) -> Void) {
        var urlRequest = urlRequest
        
        // Add JWT token to request header if available
        if let token = keychainManager.getAccessToken() {
            urlRequest.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }
        
        completion(.success(urlRequest))
    }
    
    func retry(_ request: Request, for session: Session, dueTo error: Error, completion: @escaping (RetryResult) -> Void) {
        guard let response = request.task?.response as? HTTPURLResponse,
              response.statusCode == 401 else {
            completion(.doNotRetryWithError(error))
            return
        }

        if isAuthRequest(request.request?.url?.path) {
            completion(.doNotRetryWithError(error))
            return
        }
        
        // Token expired, try to refresh
        refreshTokenSerialized { result in
            switch result {
            case .success:
                // Token refreshed successfully, retry the request
                completion(.retry)
                
            case .failure(let error):
                // Refresh failed, clear tokens and don't retry
                self.authRepository.logout()
                
                // Post notification to show login screen
                NotificationCenter.default.post(name: NSNotification.Name("UserSessionExpired"), object: nil)
                
                completion(.doNotRetryWithError(error))
            }
        }
    }

    private func refreshTokenSerialized(completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        refreshLock.lock()
        refreshCompletions.append(completion)
        if refreshInFlight {
            refreshLock.unlock()
            return
        }
        refreshInFlight = true
        refreshLock.unlock()

        authRepository.refreshToken { [weak self] result in
            guard let self = self else { return }
            self.refreshLock.lock()
            let completions = self.refreshCompletions
            self.refreshCompletions.removeAll()
            self.refreshInFlight = false
            self.refreshLock.unlock()
            completions.forEach { $0(result) }
        }
    }

    private func isAuthRequest(_ path: String?) -> Bool {
        guard let path = path else { return false }
        return path.contains("/auth/login") ||
            path.contains("/auth/register") ||
            path.contains("/auth/google") ||
            path.contains("/auth/refresh") ||
            path.contains("/auth/logout")
    }
}
