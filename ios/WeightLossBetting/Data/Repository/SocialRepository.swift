import Foundation
import Alamofire

// MARK: - Social Repository
class SocialRepository {
    private let apiService: APIService
    
    init(apiService: APIService = .shared) {
        self.apiService = apiService
    }
    
    // MARK: - Leaderboard
    
    func getWeightLossLeaderboard(limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        apiService.request<[LeaderboardEntry]>(
            endpoint: "/leaderboard/weight-loss",
            method: .get,
            parameters: ["limit": limit],
            completion: completion
        )
    }
    
    func getCheckInStreakLeaderboard(limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        apiService.request<[LeaderboardEntry]>(
            endpoint: "/leaderboard/check-in-streak",
            method: .get,
            parameters: ["limit": limit],
            completion: completion
        )
    }
    
    func getWinRateLeaderboard(limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        apiService.request<[LeaderboardEntry]>(
            endpoint: "/leaderboard/win-rate",
            method: .get,
            parameters: ["limit": limit],
            completion: completion
        )
    }
    
    // MARK: - Comments
    
    func getComments(planId: String, page: Int = 1, pageSize: Int = 20, completion: @escaping (Result<[Comment], Error>) -> Void) {
        apiService.request<[Comment]>(
            endpoint: "/betting-plans/\(planId)/comments",
            method: .get,
            parameters: ["page": page, "page_size": pageSize],
            completion: completion
        )
    }
    
    func postComment(planId: String, content: String, completion: @escaping (Result<Comment, Error>) -> Void) {
        let parameters: [String: Any] = ["content": content]
        apiService.request<Comment>(
            endpoint: "/betting-plans/\(planId)/comments",
            method: .post,
            parameters: parameters,
            completion: completion
        )
    }
    
    // MARK: - Encouragement
    
    func sendEncouragement(userId: String, completion: @escaping (Result<EncouragementResponse, Error>) -> Void) {
        apiService.request<EncouragementResponse>(
            endpoint: "/users/\(userId)/encourage",
            method: .post,
            parameters: nil,
            completion: completion
        )
    }
    
    // MARK: - Badges
    
    func getUserBadges(userId: String, completion: @escaping (Result<[Badge], Error>) -> Void) {
        apiService.request<[Badge]>(
            endpoint: "/users/\(userId)/badges",
            method: .get,
            parameters: nil,
            completion: completion
        )
    }
}

// MARK: - Models



struct Comment: Codable {
    let id: String
    let planId: String
    let userId: String
    let userNickname: String
    let content: String
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case planId = "plan_id"
        case userId = "user_id"
        case userNickname = "user_nickname"
        case content
        case createdAt = "created_at"
    }
}

struct EncouragementResponse: Codable {
    let success: Bool
    let message: String
    let remainingCount: Int
    
    enum CodingKeys: String, CodingKey {
        case success, message
        case remainingCount = "remaining_count"
    }
}
