import Foundation
import Alamofire

class RetryInterceptor: RequestInterceptor {
    private let maxRetryCount = 3
    private let initialBackoffMs: TimeInterval = 1.0
    
    func retry(_ request: Request, for session: Session, dueTo error: Error, completion: @escaping (RetryResult) -> Void) {
        guard let retryCount = request.retryCount as? Int else {
            completion(.doNotRetryWithError(error))
            return
        }
        
        // Check if we should retry
        if retryCount >= maxRetryCount {
            completion(.doNotRetryWithError(error))
            return
        }
        
        // Only retry on timeout or server errors (5xx)
        if let urlError = error as? URLError {
            if urlError.code == .timedOut {
                let backoffTime = initialBackoffMs * Double(retryCount + 1)
                completion(.retryWithDelay(backoffTime))
                return
            }
        }
        
        if let response = request.task?.response as? HTTPURLResponse {
            if (500...599).contains(response.statusCode) {
                let backoffTime = initialBackoffMs * Double(retryCount + 1)
                completion(.retryWithDelay(backoffTime))
                return
            }
        }
        
        completion(.doNotRetryWithError(error))
    }
}
