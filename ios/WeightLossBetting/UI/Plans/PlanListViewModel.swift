import Foundation

class PlanListViewModel {
    
    // MARK: - Properties
    
    private let repository = BettingPlanRepository.shared
    
    var plans: [BettingPlan] = []
    var filteredPlans: [BettingPlan] = []
    var currentFilter: PlanStatus?
    
    var onPlansUpdated: (() -> Void)?
    var onError: ((String) -> Void)?
    var onLoadingChanged: ((Bool) -> Void)?
    
    // MARK: - Public Methods
    
    func loadPlans(userId: String, status: PlanStatus? = nil, forceRefresh: Bool = false) {
        print("🔵 [PlanListVM] 开始加载计划列表，userId=\(userId), status=\(status?.rawValue ?? "全部"), forceRefresh=\(forceRefresh)")
        onLoadingChanged?(true)
        
        let statusString = status?.rawValue
        
        repository.getUserBettingPlans(userId: userId, status: statusString, forceRefresh: forceRefresh) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plans):
                    print("✅ [PlanListVM] 计划列表加载成功，共 \(plans.count) 个计划")
                    for (index, plan) in plans.enumerated() {
                        print("\n--- 计划 \(index + 1) ---")
                        print("   - 计划 ID: \(plan.id)")
                        print("   - 状态：\(plan.status.rawValue)")
                        print("   - 赌金：¥\(plan.betAmount)")
                        print("   - 创建者 ID: \(plan.creatorId ?? "nil")")
                        print("   - 创建者昵称：\(plan.creatorNickname ?? "nil")")
                        print("   - 创建者邮箱：\(plan.creatorEmail ?? "nil")")
                        print("   - 参与者 ID: \(plan.participantId ?? "nil")")
                        print("   - 参与者昵称：\(plan.participantNickname ?? "nil")")
                        print("   - 参与者邮箱：\(plan.participantEmail ?? "nil")")
                        print("   - 是否是创建者：\(plan.isCreator ? "是" : "否")")
                        print("   - 是否是参与者：\(plan.isParticipant ? "是" : "否")")
                    }
                    print("\n")
                    self?.plans = plans
                    self?.currentFilter = status
                    self?.applyFilter()
                    self?.onPlansUpdated?()
                    
                case .failure(let error):
                    print("❌ [PlanListVM] 计划列表加载失败：\(error.localizedDescription)")
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
    
    func filterPlans(by status: PlanStatus?) {
        currentFilter = status
        applyFilter()
        onPlansUpdated?()
    }
    
    private func applyFilter() {
        if let filter = currentFilter {
            filteredPlans = plans.filter { $0.status == filter }
        } else {
            filteredPlans = plans
        }
    }
}
