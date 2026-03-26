import Foundation

class CacheManager {
    static let shared = CacheManager()
    
    private let userDefaults = UserDefaults.standard
    private let coreDataManager = CoreDataManager.shared
    
    // Cache expiration times (in seconds)
    private let userCacheExpiration: TimeInterval = 600 // 10 minutes
    private let planCacheExpiration: TimeInterval = 300 // 5 minutes
    private let checkInCacheExpiration: TimeInterval = 300 // 5 minutes
    
    private init() {}
    
    // MARK: - User Caching
    
    func cacheUser(_ user: User) {
        coreDataManager.cacheUser(user)
        setCacheTimestamp(for: "user_\(user.id)")
    }
    
    func getCachedUser(id: String) -> User? {
        guard isCacheValid(for: "user_\(id)", expiration: userCacheExpiration) else {
            return nil
        }
        return coreDataManager.getCachedUser(id: id)
    }
    
    // MARK: - Betting Plan Caching
    
    func cacheBettingPlan(_ plan: BettingPlan) {
        coreDataManager.cacheBettingPlan(plan)
        setCacheTimestamp(for: "plan_\(plan.id)")
    }
    
    func cacheBettingPlans(_ plans: [BettingPlan], userId: String) {
        plans.forEach { coreDataManager.cacheBettingPlan($0) }
        setCacheTimestamp(for: "plans_\(userId)")
    }
    
    func getCachedBettingPlan(id: String) -> BettingPlan? {
        guard isCacheValid(for: "plan_\(id)", expiration: planCacheExpiration) else {
            return nil
        }
        let plans = coreDataManager.getCachedBettingPlans(userId: "")
        return plans.first { $0.id == id }
    }
    
    func getCachedBettingPlans(userId: String) -> [BettingPlan]? {
        guard isCacheValid(for: "plans_\(userId)", expiration: planCacheExpiration) else {
            return nil
        }
        return coreDataManager.getCachedBettingPlans(userId: userId)
    }
    
    // MARK: - Check-In Caching
    
    func cacheCheckIn(_ checkIn: CheckIn) {
        coreDataManager.cacheCheckIn(checkIn)
        setCacheTimestamp(for: "checkin_\(checkIn.planId)")
    }
    
    func cacheCheckIns(_ checkIns: [CheckIn], planId: String) {
        checkIns.forEach { coreDataManager.cacheCheckIn($0) }
        setCacheTimestamp(for: "checkins_\(planId)")
    }
    
    func getCachedCheckIns(planId: String) -> [CheckIn]? {
        guard isCacheValid(for: "checkins_\(planId)", expiration: checkInCacheExpiration) else {
            return nil
        }
        return coreDataManager.getCachedCheckIns(planId: planId)
    }
    
    // MARK: - Cache Validation
    
    private func setCacheTimestamp(for key: String) {
        userDefaults.set(Date(), forKey: "cache_timestamp_\(key)")
    }
    
    private func getCacheTimestamp(for key: String) -> Date? {
        return userDefaults.object(forKey: "cache_timestamp_\(key)") as? Date
    }
    
    private func isCacheValid(for key: String, expiration: TimeInterval) -> Bool {
        guard let timestamp = getCacheTimestamp(for: key) else {
            return false
        }
        
        let elapsed = Date().timeIntervalSince(timestamp)
        return elapsed < expiration
    }
    
    func invalidateCache(for key: String) {
        userDefaults.removeObject(forKey: "cache_timestamp_\(key)")
    }
    
    func invalidateAllCache() {
        let keys = userDefaults.dictionaryRepresentation().keys
        keys.filter { $0.hasPrefix("cache_timestamp_") }.forEach {
            userDefaults.removeObject(forKey: $0)
        }
        coreDataManager.clearAllCache()
    }
    
    // MARK: - Generic Caching
    
    func set<T: Codable>(_ value: T, forKey key: String, expirationMinutes: Int = 5) {
        let encoder = JSONEncoder()
        encoder.dateEncodingStrategy = .iso8601
        
        if let encoded = try? encoder.encode(value) {
            userDefaults.set(encoded, forKey: "cache_data_\(key)")
            
            // Set expiration timestamp
            let expirationDate = Date().addingTimeInterval(TimeInterval(expirationMinutes * 60))
            userDefaults.set(expirationDate, forKey: "cache_expiration_\(key)")
        }
    }
    
    func get<T: Codable>(forKey key: String) -> T? {
        // Check if cache has expired
        if let expirationDate = userDefaults.object(forKey: "cache_expiration_\(key)") as? Date {
            if Date() > expirationDate {
                // Cache expired, remove it
                userDefaults.removeObject(forKey: "cache_data_\(key)")
                userDefaults.removeObject(forKey: "cache_expiration_\(key)")
                return nil
            }
        } else {
            return nil
        }
        
        // Get cached data
        guard let data = userDefaults.data(forKey: "cache_data_\(key)") else {
            return nil
        }
        
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        
        return try? decoder.decode(T.self, from: data)
    }
    
    func remove(forKey key: String) {
        userDefaults.removeObject(forKey: "cache_data_\(key)")
        userDefaults.removeObject(forKey: "cache_expiration_\(key)")
    }
}
