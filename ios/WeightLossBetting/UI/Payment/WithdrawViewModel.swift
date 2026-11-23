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
    var onConnectOnboardingReady: ((URL) -> Void)?
    
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

    func startConnectOnboarding() {
        Task {
            let result = await paymentRepository.createConnectOnboardingLink()
            switch result {
            case .success(let onboarding):
                if let url = URL(string: onboarding.url) {
                    onConnectOnboardingReady?(url)
                } else {
                    withdrawState = .error("提现账户认证链接无效")
                }
            case .failure(let error):
                withdrawState = .error(parseError(error))
            case .loading:
                break
            }
        }
    }
    
    // MARK: - Public Methods
    
    func loadAvailableBalance() {
        balanceState = .loading
        
        guard let userId = AuthRepository.shared.getCurrentUserId(), !userId.isEmpty else {
            balanceState = .error("登录状态已失效，请重新登录")
            return
        }
        
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
    
    func withdraw(amount: Double) {
        guard amount.isFinite, amount > 0 else {
            withdrawState = .error("提现金额必须大于0")
            return
        }
        guard amount >= 0.01 else {
            withdrawState = .error("提现金额不能少于0.01元")
            return
        }
        guard amount <= 50000 else {
            withdrawState = .error("单次提现金额不能超过50000元")
            return
        }
        withdrawState = .loading
        
        Task {
            // Stripe 模式使用 Connect 账户，不再把银行卡后四位当作提现凭证。
            let result = await paymentRepository.withdraw(amount: amount, paymentMethodId: "")
            
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
