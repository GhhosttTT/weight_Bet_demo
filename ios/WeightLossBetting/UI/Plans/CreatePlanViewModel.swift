import Foundation

class CreatePlanViewModel {
    
    // MARK: - Properties
    
    private let repository = BettingPlanRepository.shared
    
    var plan: BettingPlan?
    var onSuccess: ((BettingPlan) -> Void)?
    var onError: ((String) -> Void)?
    var onLoadingChanged: ((Bool) -> Void)?
    
    // MARK: - Public Methods
    
    func createPlan(
        betAmount: String,
        startDate: Date,
        endDate: Date,
        initialWeight: String,
        targetWeight: String,
        description: String?
    ) {
        // Validate inputs
        guard let betAmountValue = Double(betAmount), betAmountValue > 0 else {
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
        let parameters: [String: Any] = [
            "bet_amount": betAmountValue,
            "start_date": dateFormatter.string(from: startDate),
            "end_date": dateFormatter.string(from: endDate),
            "creator_goal": [
                "initial_weight": initialWeightValue,
                "target_weight": targetWeightValue,
                "target_weight_loss": initialWeightValue - targetWeightValue
            ],
            "description": description ?? ""
        ]
        
        onLoadingChanged?(true)
        
        repository.createBettingPlan(parameters: parameters) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plan):
                    self?.plan = plan
                    self?.onSuccess?(plan)
                    
                case .failure(let error):
                    let errorMessage = self?.parseError(error) ?? error.localizedDescription
                    self?.onError?(errorMessage)
                }
            }
        }
    }
    
    private func parseError(_ error: Error) -> String {
        // Parse specific error messages
        let errorString = error.localizedDescription
        if errorString.contains("insufficient") || errorString.contains("余额不足") {
            return "账户余额不足,请先充值"
        }
        return errorString
    }
}
