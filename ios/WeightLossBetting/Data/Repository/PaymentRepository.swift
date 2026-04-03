import Foundation

class PaymentRepository: BaseRepository {
    static let shared = PaymentRepository()
    override init() {}
    
    private let apiService = APIService.shared
    private let cacheManager = CacheManager.shared
    
    func getBalance(userId: String, forceRefresh: Bool = false) async -> NetworkResult<Balance> {
        let cacheKey = "balance_\(userId)"
        
        // Check cache first if not forcing refresh
        if !forceRefresh, let cachedBalance: Balance = cacheManager.get(forKey: cacheKey) {
            return .success(cachedBalance)
        }
        
        let result = await safeApiCall { completion in
            self.apiService.getBalance(userId: userId, completion: completion)
        }
        
        // Cache successful result
        if case .success(let balance) = result {
            cacheManager.set(balance, forKey: cacheKey, expirationMinutes: 1)
        }
        
        return result
    }
    
    func getTransactionHistory(userId: String, forceRefresh: Bool = false) async -> NetworkResult<[Transaction]> {
        let cacheKey = "transactions_\(userId)"
        
        // Check cache first if not forcing refresh
        if !forceRefresh, let cachedTransactions: [Transaction] = cacheManager.get(forKey: cacheKey) {
            return .success(cachedTransactions)
        }
        
        let result = await safeApiCall { completion in
            self.apiService.getTransactionHistory(userId: userId, completion: completion)
        }
        
        // Cache successful result
        if case .success(let transactions) = result {
            cacheManager.set(transactions, forKey: cacheKey, expirationMinutes: 5)
        }
        
        return result
    }
    
    func charge(amount: Double, paymentMethodId: String) async -> NetworkResult<ChargeResult> {
        let result = await safeApiCall { completion in
            self.apiService.charge(amount: amount, paymentMethodId: paymentMethodId, completion: completion)
        }
            
        return result
    }
    
    func withdraw(amount: Double, bankAccount: BankAccount) async -> NetworkResult<WithdrawResult> {
        let result = await safeApiCall { completion in
            self.apiService.withdraw(amount: amount, completion: completion)
        }
            
        return result
    }
}
