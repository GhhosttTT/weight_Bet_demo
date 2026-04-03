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
    var onBalanceRefreshWarning: (() -> Void)?

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
                print("✅ [ChargeVM] 充值成功：金额=¥\(chargeResult.amount), 新余额=¥\(chargeResult.newBalance ?? 0)")
                
                // 与安卓端保持一致：充值成功后清除所有缓存
                print("🔄 [ChargeVM] 开始清除所有缓存...")
                CacheManager.shared.invalidateAllCache()
                print("✅ [ChargeVM] 缓存已清除")
                
                // ✅ 后端已返回新余额，直接使用
                if let userId = AuthRepository.shared.getCurrentUserId() {
                    print("🔄 [ChargeVM] 开始更新余额缓存...")
                    
                    // 优先使用后端返回的新余额
                    if let newBalanceFromServer = chargeResult.newBalance {
                        let newBalance = Balance(
                            userId: userId,
                            availableBalance: newBalanceFromServer,
                            frozenBalance: 0.0,
                            updatedAt: Date()
                        )
                        CacheManager.shared.set(newBalance, forKey: "balance_\(userId)", expirationMinutes: 5)
                        print("✅ [ChargeVM] 已更新余额缓存：¥\(newBalanceFromServer)")
                    } else {
                        // 如果后端没有返回 new_balance，使用本地计算
                        print("⚠️ [ChargeVM] 后端未返回新余额，使用本地计算...")
                        let currentBalance: Balance?
                        if let cached: Balance = CacheManager.shared.get(forKey: "balance_\(userId)") {
                            print("💰 [ChargeVM] 从缓存获取到余额：¥\(cached.availableBalance)")
                            currentBalance = cached
                        } else {
                            currentBalance = nil
                        }
                        
                        let oldBalance = currentBalance?.availableBalance ?? 0.0
                        let newBalanceValue = oldBalance + chargeResult.amount
                        
                        let newBalance = Balance(
                            userId: userId,
                            availableBalance: newBalanceValue,
                            frozenBalance: currentBalance?.frozenBalance ?? 0.0,
                            updatedAt: Date()
                        )
                        CacheManager.shared.set(newBalance, forKey: "balance_\(userId)", expirationMinutes: 5)
                        print("✅ [ChargeVM] 已手动计算并更新余额：¥\(newBalanceValue)")
                    }
                    
                    // 异步调用后端 API 刷新余额（确保数据一致）
                    Task {
                        let paymentRepo = PaymentRepository()
                        let result = await paymentRepo.getBalance(userId: userId, forceRefresh: true)
                        
                        switch result {
                        case .success(let balance):
                            print("✅ [ChargeVM] 后端返回最新余额：可用余额=¥\(balance.availableBalance)")
                            CacheManager.shared.set(balance, forKey: "balance_\(userId)", expirationMinutes: 5)
                        case .failure(let error):
                            print("⚠️ [ChargeVM] 后端余额刷新失败：\(error.localizedDescription)，继续使用缓存")
                        case .loading:
                            break
                        }
                    }
                } else {
                    print("⚠️ [ChargeVM] 无法获取当前用户 ID，跳过余额刷新")
                }
                
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

    private func showBalanceRefreshWarning() {
        onBalanceRefreshWarning?()
    }
}
