import Foundation

class RecommendationRepository {
    static let shared = RecommendationRepository()
    
    private let apiService = APIService.shared
    private let cacheManager = RecommendationCacheManager.shared
    
    private init() {}
    
    // MARK: - Recommendation
    
    func getRecommendation(useCache: Bool = true, completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        // If useCache is true and cache exists, return cached data immediately
        if useCache, let cachedRecommendation = cacheManager.getCachedRecommendation() {
            print("✅ [RecommendationRepo] Returning cached recommendation")
            completion(.success(cachedRecommendation))
            return
        }
        
        // Fetch from API
        print("🔵 [RecommendationRepo] Fetching from API...")
        apiService.getRecommendation(useCache: useCache) { [weak self] result in
            switch result {
            case .success(let recommendation):
                // Cache the new recommendation
                self?.cacheManager.cacheRecommendation(recommendation)
                completion(.success(recommendation))
                
            case .failure(let error):
                // If API fails and we have cache, return cached data
                if useCache, let cachedRecommendation = self?.cacheManager.getCachedRecommendation() {
                    print("⚠️ [RecommendationRepo] API failed, returning cached recommendation")
                    completion(.success(cachedRecommendation))
                } else {
                    completion(.failure(error))
                }
            }
        }
    }
    
    func refreshRecommendation(completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        apiService.refreshRecommendation { [weak self] result in
            switch result {
            case .success(let recommendation):
                // Cache the refreshed recommendation
                self?.cacheManager.cacheRecommendation(recommendation)
                completion(.success(recommendation))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Cache Management
    
    func preloadRecommendation() {
        // Preload recommendation in background without callback
        apiService.getRecommendation(useCache: false) { [weak self] result in
            switch result {
            case .success(let recommendation):
                self?.cacheManager.cacheRecommendation(recommendation)
                print("✅ [RecommendationRepo] Preloaded recommendation in background")
                
            case .failure(let error):
                print("⚠️ [RecommendationRepo] Failed to preload recommendation: \(error.localizedDescription)")
            }
        }
    }
}
