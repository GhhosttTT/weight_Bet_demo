import Foundation

class RecommendationCacheManager {
    static let shared = RecommendationCacheManager()
    
    private let userDefaults: UserDefaults
    private let cacheKey = "cached_recommendation"
    private let cacheTimestampKey = "cached_recommendation_timestamp"
    private let maxCacheAge: TimeInterval = 24 * 60 * 60 // 24 hours
    
    private init() {
        userDefaults = UserDefaults.standard
    }
    
    // MARK: - Cache Management
    
    /// Cache recommendation data
    func cacheRecommendation(_ recommendation: RecommendationResponse) {
        do {
            let encoder = JSONEncoder()
            encoder.dateEncodingStrategy = .iso8601
            let data = try encoder.encode(recommendation)
            userDefaults.set(data, forKey: cacheKey)
            userDefaults.set(Date().timeIntervalSince1970, forKey: cacheTimestampKey)
            print("✅ [CacheManager] Recommendation cached successfully")
        } catch {
            print("❌ [CacheManager] Failed to encode recommendation: \(error.localizedDescription)")
        }
    }
    
    /// Get cached recommendation if available and not expired
    func getCachedRecommendation() -> RecommendationResponse? {
        guard let data = userDefaults.data(forKey: cacheKey) else {
            return nil
        }
        
        // Check if cache is expired
        if isCacheExpired() {
            print("⚠️ [CacheManager] Cache expired, clearing...")
            clearCache()
            return nil
        }
        
        do {
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            let recommendation = try decoder.decode(RecommendationResponse.self, from: data)
            print("✅ [CacheManager] Retrieved cached recommendation")
            return recommendation
        } catch {
            print("❌ [CacheManager] Failed to decode cached recommendation: \(error.localizedDescription)")
            clearCache()
            return nil
        }
    }
    
    /// Check if cache is expired
    func isCacheExpired() -> Bool {
        guard let timestamp = userDefaults.object(forKey: cacheTimestampKey) as? TimeInterval else {
            return true // No timestamp means no cache
        }
        
        let age = Date().timeIntervalSince1970 - timestamp
        return age > maxCacheAge
    }
    
    /// Clear cached recommendation
    func clearCache() {
        userDefaults.removeObject(forKey: cacheKey)
        userDefaults.removeObject(forKey: cacheTimestampKey)
        print("🗑️ [CacheManager] Cache cleared")
    }
    
    /// Check if cache exists
    func hasCache() -> Bool {
        return userDefaults.object(forKey: cacheKey) != nil
    }
}
