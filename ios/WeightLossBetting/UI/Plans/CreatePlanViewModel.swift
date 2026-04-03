import Foundation

class CreatePlanViewModel {
    
    // MARK: - Properties
    
    private let repository = BettingPlanRepository.shared
    
    var plan: BettingPlan?
    var onSuccess: ((BettingPlan) -> Void)?
    var onError: ((String) -> Void)?
    var onInsufficientBalance: ((Double) -> Void)?  // 余额不足时触发，传递需要的金额
    var onLoadingChanged: ((Bool) -> Void)?
    
    // MARK: - Public Methods
    
    /// 检查余额（用于充值成功后刷新）
    func checkBalance(forceRefresh: Bool = false) {
        print("💰 [CreatePlanVM] 检查余额，forceRefresh=\(forceRefresh)")
        // 这个方法主要用于触发余额刷新，实际刷新逻辑在 CacheManager 和 Repository
        // 充值成功后调用此方法，清除缓存即可
    }
    
    func createPlan(
        betAmount: String,
        startDate: Date,
        endDate: Date,
        initialWeight: String,
        targetWeight: String,
        description: String?,
        inviteeId: String? = nil
    ) {
        print("🚀 [CreatePlanVM] 开始创建计划...")
        print("   - 赌金：¥\(betAmount)")
        print("   - 开始日期：\(startDate)")
        print("   - 结束日期：\(endDate)")
        if let inviteeId = inviteeId {
            print("   - 被邀请人 ID: \(inviteeId)")
        }
        
        // Validate inputs
        guard let betAmountValue = Double(betAmount), betAmountValue > 0 else {
            print("❌ [CreatePlanVM] 赌金金额无效")
            onError?("请输入有效的赌金金额")
            return
        }
        
        guard let initialWeightValue = Double(initialWeight), initialWeightValue >= 30, initialWeightValue <= 300 else {
            onError?("初始体重必须在 30-300 kg 之间")
            return
        }
        
        guard let targetWeightValue = Double(targetWeight), targetWeightValue >= 30, targetWeightValue <= 300 else {
            onError?("目标体重必须在 30-300 kg 之间")
            return
        }
        
        guard targetWeightValue < initialWeightValue else {
            onError?("目标体重必须小于初始体重")
            return
        }
        
        guard endDate > startDate else {
            onError?("结束日期必须晚于开始日期")
            return
        }
        
        let daysDiff = Calendar.current.dateComponents([.day], from: startDate, to: endDate).day ?? 0
        guard daysDiff >= 1 && daysDiff <= 365 else {
            onError?("计划时长必须在 1-365 天之间")
            return
        }
        
        // Create parameters
        let dateFormatter = ISO8601DateFormatter()
        var parameters: [String: Any] = [
            "bet_amount": betAmountValue,
            "start_date": dateFormatter.string(from: startDate),
            "end_date": dateFormatter.string(from: endDate),
            "initial_weight": initialWeightValue,
            "target_weight": targetWeightValue,
            "description": description ?? ""
        ]
        
        // Add invitee_id if provided
        if let inviteeId = inviteeId {
            parameters["invitee_id"] = inviteeId
            print("📧 [CreatePlanVM] 添加被邀请人 ID: \(inviteeId)")
        }

        print("📡 [CreatePlanVM] 发送创建计划请求到后端...")
        onLoadingChanged?(true)
        
        repository.createBettingPlan(parameters: parameters) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plan):
                    print("✅ [CreatePlanVM] 计划创建成功！planId=\(plan.id)")
                    self?.plan = plan
                    self?.onSuccess?(plan)
                    
                    // 发送通知，刷新计划列表
                    NotificationCenter.default.post(name: NSNotification.Name(rawValue: "plansUpdated"), object: nil)
                    print("📢 [CreatePlanVM] 已发送 plansUpdated 通知")
                    
                case .failure(let error):
                    print("❌ [CreatePlanVM] 计划创建失败：\(error.localizedDescription)")
                    // Check if it's an insufficient balance error
                    if self?.isInsufficientBalanceError(error) == true {
                        let amountNeeded = self?.extractAmountNeeded(from: error) ?? betAmountValue
                        print("💰 [CreatePlanVM] 检测到余额不足，需要充值：¥\(amountNeeded)")
                        self?.onInsufficientBalance?(amountNeeded)
                    } else {
                        let errorMessage = self?.parseError(error) ?? error.localizedDescription
                        self?.onError?(errorMessage)
                    }
                }
            }
        }
    }
    
    private func isInsufficientBalanceError(_ error: Error) -> Bool {
        let errorString = error.localizedDescription
        print("🔍 Checking error: \(errorString)")
        
        // Check for various insufficient balance indicators
        if errorString.contains("insufficient") || 
           errorString.contains("余额不足") || 
           errorString.contains("402") {
            print("✅ Detected insufficient balance error")
            return true
        }
        
        // Try to parse nested error from response body
        if let networkError = error as? NetworkError {
            switch networkError {
            case .serverError(_, let message):
                if message.contains("余额不足") || message.contains("insufficient") {
                    print("✅ Detected insufficient balance from server message: \(message)")
                    return true
                }
            case .unknownError(let message):
                if message.contains("余额不足") {
                    print("✅ Detected insufficient balance from unknown error: \(message)")
                    return true
                }
            default:
                break
            }
        }
        
        return false
    }
        
    private func extractAmountNeeded(from error: Error) -> Double? {
        print("💰 Trying to extract amount from error...")
        
        let pattern = "\\d+\\.?\\d*"
        
        // Try to extract from nested NetworkError first
        if let networkError = error as? NetworkError {
            switch networkError {
            case .serverError(_, let message):
                // Server message contains the actual amount, e.g., "余额不足，需要充值 200.0 元"
                if let range = message.range(of: pattern, options: .regularExpression),
                   let amount = Double(message[range]) {
                    print("✅ Extracted amount from server message: \(amount)")
                    return amount
                }
            case .unknownError(let message):
                if let range = message.range(of: pattern, options: .regularExpression),
                   let amount = Double(message[range]) {
                    print("✅ Extracted amount from unknown error: \(amount)")
                    return amount
                }
            default:
                break
            }
        }
        
        // Fallback: try to extract from localizedDescription
        let errorString = error.localizedDescription
        print("⚠️ Falling back to localizedDescription: \(errorString)")
        if let range = errorString.range(of: pattern, options: .regularExpression),
           let amount = Double(errorString[range]) {
            print("⚠️ Extracted amount from error string (may be inaccurate): \(amount)")
            return amount
        }
        
        print("❌ Could not extract amount")
        return nil
    }
        
    private func parseError(_ error: Error) -> String {
        // Parse specific error messages
        let errorString = error.localizedDescription
        if errorString.contains("insufficient") || errorString.contains("余额不足") {
            return "账户余额不足，请先充值"
        }
        return errorString
    }
}
