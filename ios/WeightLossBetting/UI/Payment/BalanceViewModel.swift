import Foundation

enum BalanceState {
    case idle
    case loading
    case success(Balance)
    case error(String)
}

enum TransactionsState {
    case idle
    case loading
    case success([Transaction])
    case error(String)
}

class BalanceViewModel {
    
    // MARK: - Properties
    
    private let paymentRepository = PaymentRepository()
    
    var onBalanceStateChanged: ((BalanceState) -> Void)?
    var onTransactionsStateChanged: ((TransactionsState) -> Void)?
    
    private var balanceState: BalanceState = .idle {
        didSet {
            onBalanceStateChanged?(balanceState)
        }
    }
    
    private var transactionsState: TransactionsState = .idle {
        didSet {
            onTransactionsStateChanged?(transactionsState)
        }
    }
    
    // MARK: - Public Methods
    
    func loadBalance(userId: String, forceRefresh: Bool = false) {
        balanceState = .loading
        
        Task {
            let result = await paymentRepository.getBalance(userId: userId, forceRefresh: forceRefresh)
            
            switch result {
            case .success(let balance):
                balanceState = .success(balance)
                
            case .failure(let error):
                let errorMessage = parseError(error)
                balanceState = .error(errorMessage)
            }
        }
    }
    
    func loadTransactions(userId: String, forceRefresh: Bool = false) {
        transactionsState = .loading
        
        Task {
            let result = await paymentRepository.getTransactionHistory(userId: userId, forceRefresh: forceRefresh)
            
            switch result {
            case .success(let transactions):
                transactionsState = .success(transactions)
                
            case .failure(let error):
                let errorMessage = parseError(error)
                transactionsState = .error(errorMessage)
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
