import Foundation
import Alamofire

final class ErrorInterceptor: EventMonitor {
    let queue = DispatchQueue(label: "com.weightloss.betting.errorInterceptor")
    
    func request<Value>(_ request: DataRequest, didParseResponse response: DataResponse<Value, AFError>) {
        guard let httpResponse = response.response else { return }
        
        // Log errors for debugging
        if !httpResponse.isSuccessful {
            print("❌ Error Response:")
            print("   URL: \(request.request?.url?.absoluteString ?? "unknown")")
            print("   Status Code: \(httpResponse.statusCode)")
            
            if let data = response.data,
               let errorString = String(data: data, encoding: .utf8) {
                print("   Error Body: \(errorString)")
            }
        }
    }
}

extension HTTPURLResponse {
    var isSuccessful: Bool {
        return (200...299).contains(statusCode)
    }
}
