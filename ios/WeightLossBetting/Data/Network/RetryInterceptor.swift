import Foundation
import Alamofire

final class RetryInterceptor: RequestInterceptor {
    private let maxRetryCount = 3
    private let initialBackoffMs: TimeInterval = 1.0
    
    func retry(_ request: Request, for session: Session, dueTo error: Error, completion: @escaping (RetryResult) -> Void) {
        // POST/PUT/DELETE 请求不重试（非幂等），避免重复提交
        if let httpMethod = request.request?.httpMethod,
           ["POST", "PUT", "DELETE", "PATCH"].contains(httpMethod.uppercased()) {
            completion(.doNotRetryWithError(error))
            return
        }
        
        guard let retryCount = request.retryCount as? Int else {
            completion(.doNotRetryWithError(error))
            return
        }
        
        // Check if we should retry
        if retryCount >= maxRetryCount {
            completion(.doNotRetryWithError(error))
            return
        }
        
        // Only retry GET on timeout or server errors (5xx)
        if let urlError = error as? URLError, urlError.code == .timedOut {
            let backoffTime = initialBackoffMs * Double(retryCount + 1)
            completion(.retryWithDelay(backoffTime))
            return
        }
        
        if let response = request.task?.response as? HTTPURLResponse,
           (500...599).contains(response.statusCode) {
            let backoffTime = initialBackoffMs * Double(retryCount + 1)
            completion(.retryWithDelay(backoffTime))
            return
        }
        
        completion(.doNotRetryWithError(error))
    }
}
