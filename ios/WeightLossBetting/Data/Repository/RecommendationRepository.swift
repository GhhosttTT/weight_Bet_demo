import Foundation

class RecommendationRepository {
    static let shared = RecommendationRepository()
    
    private let apiService = APIService.shared
    
    private init() {}
    
    // MARK: - Recommendation
    
    func getRecommendation(useCache: Bool = true, completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        apiService.getRecommendation(useCache: useCache, completion: completion)
    }
    
    func refreshRecommendation(completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        apiService.refreshRecommendation(completion: completion)
    }
}
