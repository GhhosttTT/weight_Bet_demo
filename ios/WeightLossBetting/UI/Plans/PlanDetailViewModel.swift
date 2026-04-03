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
    var onPaymentRequired: ((Double) -> Void)? // 余额不足时回调，参数为需要充值的金额
    
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
                    
                    // 不再单独调用用户接口，直接使用 plan 中的 participantNickname 和 participantEmail
                    // 后端已在计划详情接口中返回了参与者的昵称和邮箱
                    
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
        
        // 后端期望的参数格式：扁平结构
        // {
        //   "initial_weight": 60,
        //   "target_weight": 55
        // }
        let parameters: [String: Any] = [
            "initial_weight": initialWeightValue,
            "target_weight": targetWeightValue
        ]
        
        onLoadingChanged?(true)
        
        repository.acceptBettingPlan(planId: planId, parameters: parameters) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plan):
                    self?.plan = plan
                    self?.onActionSuccess?("计划接受成功")
                    self?.onPlanUpdated?(plan)
                    
                case .failure(let error):
                    // 先获取原始错误消息（不要调用parseError修改）
                    let rawErrorStr = error.localizedDescription
                    
                    // 409错误表示计划已被接受，视为成功
                    if rawErrorStr.contains("409") || rawErrorStr.contains("已被其他用户接受") {
                        self?.onActionSuccess?("计划接受成功")
                        return
                    }
                    
                    // 402错误表示余额不足，兜底逻辑（预校验已经处理了大部分情况，这里是兜底）
                    if rawErrorStr.range(of: "402", options: .caseInsensitive) != nil {
                        let requiredAmount = self?.plan?.betAmount ?? 1.0
                        self?.onPaymentRequired?(requiredAmount)
                        return // 直接返回，不弹普通错误提示
                    }
                    
                    // 其他错误调用parseError处理
                    let errorMessage = self?.parseError(error) ?? rawErrorStr
                    self?.onError?(errorMessage)
                }
            }
        }
    }
    
    func confirmPlan() {
        onLoadingChanged?(true)
        
        repository.confirmBettingPlan(planId: planId) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plan):
                    self?.plan = plan
                    self?.onActionSuccess?("计划已确认，开始生效")
                    self?.onPlanUpdated?(plan)
                    
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
                    self?.loadPlanDetail(forceRefresh: true)
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
    
    func cancelPlan() {
        onLoadingChanged?(true)
        
        repository.cancelBettingPlan(planId: planId) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success:
                    self?.onActionSuccess?("计划已取消，赌金已返还")
                    self?.loadPlanDetail(forceRefresh: true)
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
    
    func giveUpPlan() {
        onLoadingChanged?(true)
        
        repository.giveUpBettingPlan(planId: planId) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success:
                    self?.onActionSuccess?("你已放弃本计划，视为认输")
                    self?.loadPlanDetail(forceRefresh: true)
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
    
    func abandonPlan(confirmation: Bool) {
        onLoadingChanged?(true)
        
        repository.abandonPlan(planId: planId, confirmation: confirmation) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let abandonResult):
                    self?.onActionSuccess?(abandonResult.message)
                    self?.loadPlanDetail(forceRefresh: true)
                    
                case .failure(let error):
                    let errorMessage = self?.parseError(error) ?? error.localizedDescription
                    self?.onError?(errorMessage)
                }
            }
        }
    }
    
    // MARK: - User Info Accessors
    
    func getCreatorNicknameAndEmail() -> (String?, String?) {
        // 直接使用 plan 中的缓存数据（后端已填充）
        return (plan?.creatorNickname, plan?.creatorEmail)
    }
    
    func getParticipantNicknameAndEmail() -> (String?, String?) {
        // 直接使用 plan 中的缓存数据（后端已填充）
        return (plan?.participantNickname, plan?.participantEmail)
    }
    
    private func parseError(_ error: Error) -> String {
        let errorString = error.localizedDescription
        if errorString.contains("insufficient") || errorString.contains("余额不足") {
            return "账户余额不足,请先充值"
        }
        return errorString
    }
}
