import Foundation

enum ChargeState {
    case idle
    case loading
    case success(ChargeResult)
    case error(String)
}

class ChargeViewModel {
    
    // MARK: - Properties
    
    private let paymentRepository = PaymentRepository()
    
    var onChargeStateChanged: ((ChargeState) -> Void)?
    
    private var chargeState: ChargeState = .idle {
        didSet {
            onChargeStateChanged?(chargeState)
        }
    }
    
    // MARK: - Public Methods
    
    func charge(amount: Double, paymentMethodId: String) {
        chargeState = .loading
        
        Task {
            let result = await paymentRepository.charge(amount: amount, paymentMethodId: paymentMethodId)
            
            switch result {
            case .success(let chargeResult):
                chargeState = .success(chargeResult)
                
            case .failure(let error):
                let errorMessage = parseError(error)
                chargeState = .error(errorMessage)
                
            case .loading:
                // Loading state is already handled before making the request
                break
            }
        }
    }
    
    // MARK: - Helper Methods
    
    private func parseError(_ error: Error) -> String {
        if let networkError = error as? NetworkError {
            switch networkError {
            case .networkError(let message):
                return "网络错误: \(message)"
            case .unauthorizedError:
                return "未授权,请重新登录"
            case .validationError(let message):
                return "验证错误: \(message)"
            case .serverError(_, let message):
                return "服务器错误: \(message)"
            case .timeoutError(let message):
                return "请求超时: \(message)"
            case .unknownError(let message):
                return message
            }
        }
        return error.localizedDescription
    }
}
