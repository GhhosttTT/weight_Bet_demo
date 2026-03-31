import Foundation

class CoachViewModel {
    private let recommendationRepository = RecommendationRepository.shared
    
    // MARK: - Load Recommendation
    
    func loadRecommendation(useCache: Bool = true, completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        recommendationRepository.getRecommendation(useCache: useCache, completion: completion)
    }
    
    func refreshRecommendation(completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        recommendationRepository.refreshRecommendation(completion: completion)
    }
    
    // MARK: - Helper Methods
    
    func getIntensityText(_ intensity: String) -> String {
        switch intensity.lowercased() {
        case "low":
            return "低强度"
        case "medium":
            return "中强度"
        case "high":
            return "高强度"
        default:
            return intensity
        }
    }
    
    func getMealTypeText(_ mealType: String) -> String {
        switch mealType.lowercased() {
        case "breakfast":
            return "早餐"
        case "lunch":
            return "午餐"
        case "dinner":
            return "晚餐"
        case "snack":
            return "加餐"
        default:
            return mealType
        }
    }
}
