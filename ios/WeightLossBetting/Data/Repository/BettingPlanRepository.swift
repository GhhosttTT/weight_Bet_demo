import Foundation

class BettingPlanRepository {
    static let shared = BettingPlanRepository()
    
    private let apiService = APIService.shared
    private let cacheManager = CacheManager.shared
    
    private init() {}
    
    // MARK: - Betting Plans
    
    func createBettingPlan(parameters: [String: Any], completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        apiService.createBettingPlan(parameters: parameters) { [weak self] result in
            switch result {
            case .success(let plan):
                // Cache the new plan
                self?.cacheManager.cacheBettingPlan(plan)
                completion(.success(plan))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func getBettingPlan(planId: String, forceRefresh: Bool = false, completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        // Try cache first if not forcing refresh
        if !forceRefresh, let cachedPlan = cacheManager.getCachedBettingPlan(id: planId) {
            completion(.success(cachedPlan))
            return
        }
        
        // Fetch from API
        apiService.getBettingPlan(planId: planId) { [weak self] result in
            switch result {
            case .success(let plan):
                // Cache the result
                self?.cacheManager.cacheBettingPlan(plan)
                completion(.success(plan))
                
            case .failure(let error):
                // If API fails, try to return cached data
                if let cachedPlan = self?.cacheManager.getCachedBettingPlan(id: planId) {
                    completion(.success(cachedPlan))
                } else {
                    completion(.failure(error))
                }
            }
        }
    }
    
    func getUserBettingPlans(userId: String, status: String? = nil, forceRefresh: Bool = false, completion: @escaping (Result<[BettingPlan], Error>) -> Void) {
        // Try cache first if not forcing refresh
        if !forceRefresh, let cachedPlans = cacheManager.getCachedBettingPlans(userId: userId) {
            let filteredPlans = status != nil ? cachedPlans.filter { $0.status.rawValue == status } : cachedPlans
            completion(.success(filteredPlans))
            return
        }
        
        // Fetch from API
        apiService.getUserBettingPlans(userId: userId, status: status) { [weak self] result in
            switch result {
            case .success(let plans):
                // Cache the results
                self?.cacheManager.cacheBettingPlans(plans, userId: userId)
                completion(.success(plans))
                
            case .failure(let error):
                // If API fails, try to return cached data
                if let cachedPlans = self?.cacheManager.getCachedBettingPlans(userId: userId) {
                    let filteredPlans = status != nil ? cachedPlans.filter { $0.status.rawValue == status } : cachedPlans
                    completion(.success(filteredPlans))
                } else {
                    completion(.failure(error))
                }
            }
        }
    }
    
    func acceptBettingPlan(planId: String, parameters: [String: Any], completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        apiService.acceptBettingPlan(planId: planId, parameters: parameters) { [weak self] result in
            switch result {
            case .success(let plan):
                // Update cache
                self?.cacheManager.cacheBettingPlan(plan)
                completion(.success(plan))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func rejectBettingPlan(planId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        apiService.rejectBettingPlan(planId: planId) { [weak self] result in
            if case .success = result {
                // Invalidate cache
                self?.cacheManager.invalidateCache(for: "plan_\(planId)")
            }
            completion(result)
        }
    }
    
    func cancelBettingPlan(planId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        apiService.cancelBettingPlan(planId: planId) { [weak self] result in
            if case .success = result {
                // Invalidate cache
                self?.cacheManager.invalidateCache(for: "plan_\(planId)")
            }
            completion(result)
        }
    }
    
    func inviteParticipant(planId: String, inviteeId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        apiService.inviteParticipant(planId: planId, inviteeId: inviteeId, completion: completion)
    }
}
