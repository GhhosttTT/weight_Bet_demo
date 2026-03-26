import Foundation
import Alamofire

class AuthInterceptor: RequestInterceptor {
    private let keychainManager = KeychainManager.shared
    private let authRepository = AuthRepository.shared
    
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
        
        // Token expired, try to refresh
        authRepository.refreshToken { result in
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
}
