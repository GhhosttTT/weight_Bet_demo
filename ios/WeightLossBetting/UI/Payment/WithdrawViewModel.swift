import Foundation

enum WithdrawState {
    case idle
    case loading
    case success(WithdrawResult)
    case error(String)
}

class WithdrawViewModel {
    
    // MARK: - Properties
    
    private let paymentRepository = PaymentRepository()
    
    var onBalanceStateChanged: ((BalanceState) -> Void)?
    var onWithdrawStateChanged: ((WithdrawState) -> Void)?
    var onAvailableBalanceUpdated: ((Double) -> Void)?
    
    private var balanceState: BalanceState = .idle {
        didSet {
            onBalanceStateChanged?(balanceState)
        }
    }
    
    private var withdrawState: WithdrawState = .idle {
        didSet {
            onWithdrawStateChanged?(withdrawState)
        }
    }
    
    var availableBalance: Double = 0.0
    
    // MARK: - Public Methods
    
    func loadAvailableBalance() {
        balanceState = .loading
        
        // TODO: 实际应用中应该使用真实的用户ID
        let userId = "current_user"
        
        Task {
            let result = await paymentRepository.getBalance(userId: userId)
            
            switch result {
            case .success(let balance):
                availableBalance = balance.availableBalance
                onAvailableBalanceUpdated?(balance.availableBalance)
                balanceState = .success(balance)
                
            case .failure(let error):
                let errorMessage = parseError(error)
                balanceState = .error(errorMessage)
            case .loading:
                break
            }
        }
    }
    
    func withdraw(amount: Double, bankAccount: BankAccount) {
        withdrawState = .loading
        
        Task {
            let result = await paymentRepository.withdraw(amount: amount, bankAccount: bankAccount)
            
            switch result {
            case .success(let withdrawResult):
                // 更新可用余额
                availableBalance -= amount
                onAvailableBalanceUpdated?(availableBalance)
                withdrawState = .success(withdrawResult)
                
            case .failure(let error):
                let errorMessage = parseError(error)
                withdrawState = .error(errorMessage)
            case .loading:
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
