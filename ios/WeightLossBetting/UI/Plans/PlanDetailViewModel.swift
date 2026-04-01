import Foundation

class PlanDetailViewModel {
    
    // MARK: - Properties
    
    private let repository = BettingPlanRepository.shared
    private var planId: String
    
    var plan: BettingPlan?
    
    var onPlanUpdated: ((BettingPlan) -> Void)?
    var onError: ((String) -> Void)?
    var onLoadingChanged: ((Bool) -> Void)?
    var onActionSuccess: ((String) -> Void)?
    
    // MARK: - Initialization
    
    init(planId: String = "") {
        self.planId = planId
    }
    
    // MARK: - Public Methods
    
    func setPlanId(_ planId: String) {
        self.planId = planId
    }
    
    func loadPlanDetail(forceRefresh: Bool = false) {
        onLoadingChanged?(true)
        
        repository.getBettingPlan(planId: planId, forceRefresh: forceRefresh) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plan):
                    self?.plan = plan
                    self?.onPlanUpdated?(plan)
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
    
    func acceptPlan(initialWeight: String, targetWeight: String) {
        // Validate inputs
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
        
        let parameters: [String: Any] = [
            "participant_goal": [
                "initial_weight": initialWeightValue,
                "target_weight": targetWeightValue,
                "target_weight_loss": initialWeightValue - targetWeightValue
            ]
        ]
        
        onLoadingChanged?(true)
        
        repository.acceptBettingPlan(planId: planId, parameters: parameters) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plan):
                    self?.plan = plan
                    self?.onActionSuccess?("计划接受成功")
                    
                case .failure(let error):
                    let errorMessage = self?.parseError(error) ?? error.localizedDescription
                    self?.onError?(errorMessage)
                }
            }
        }
    }
    
    func rejectPlan() {
        onLoadingChanged?(true)
        
        repository.rejectBettingPlan(planId: planId) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success:
                    self?.onActionSuccess?("计划已拒绝")
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
    
    private func parseError(_ error: Error) -> String {
        let errorString = error.localizedDescription
        if errorString.contains("insufficient") || errorString.contains("余额不足") {
            return "账户余额不足,请先充值"
        }
        return errorString
    }
}
