import Foundation
import Alamofire

final class ErrorInterceptor: EventMonitor {
    let queue = DispatchQueue(label: "com.weightloss.betting.errorInterceptor")
    
    func request<Value>(_ request: DataRequest, didParseResponse response: DataResponse<Value, AFError>) {
        guard let httpResponse = response.response else { return }
        
        // Log errors for debugging
        if !httpResponse.isSuccessful {
            // Avoid logging URLs, query parameters, authorization data, or bodies.
            print("❌ Network request failed (HTTP \(httpResponse.statusCode))")
        }
    }
}

extension HTTPURLResponse {
    var isSuccessful: Bool {
        return (200...299).contains(statusCode)
    }
}
