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
        onLoadingChanged?(true)
        
        let statusString = status?.rawValue
        
        repository.getUserBettingPlans(userId: userId, status: statusString, forceRefresh: forceRefresh) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let plans):
                    self?.plans = plans
                    self?.currentFilter = status
                    self?.applyFilter()
                    self?.onPlansUpdated?()
                    
                case .failure(let error):
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
