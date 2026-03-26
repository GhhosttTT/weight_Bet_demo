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
        apiService.request(
            endpoint: "/leaderboard/weight-loss",
            method: .get,
            parameters: ["limit": limit],
            completion: completion
        )
    }
    
    func getCheckInStreakLeaderboard(limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        apiService.request(
            endpoint: "/leaderboard/check-in-streak",
            method: .get,
            parameters: ["limit": limit],
            completion: completion
        )
    }
    
    func getWinRateLeaderboard(limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        apiService.request(
            endpoint: "/leaderboard/win-rate",
            method: .get,
            parameters: ["limit": limit],
            completion: completion
        )
    }
    
    // MARK: - Comments
    
    func getComments(planId: String, page: Int = 1, pageSize: Int = 20, completion: @escaping (Result<[Comment], Error>) -> Void) {
        apiService.request(
            endpoint: "/betting-plans/\(planId)/comments",
            method: .get,
            parameters: ["page": page, "page_size": pageSize],
            completion: completion
        )
    }
    
    func postComment(planId: String, content: String, completion: @escaping (Result<Comment, Error>) -> Void) {
        let parameters: [String: Any] = ["content": content]
        apiService.request(
            endpoint: "/betting-plans/\(planId)/comments",
            method: .post,
            parameters: parameters,
            completion: completion
        )
    }
    
    // MARK: - Encouragement
    
    func sendEncouragement(userId: String, completion: @escaping (Result<EncouragementResponse, Error>) -> Void) {
        apiService.request(
            endpoint: "/users/\(userId)/encourage",
            method: .post,
            parameters: nil,
            completion: completion
        )
    }
    
    // MARK: - Badges
    
    func getUserBadges(userId: String, completion: @escaping (Result<[Badge], Error>) -> Void) {
        apiService.request(
            endpoint: "/users/\(userId)/badges",
            method: .get,
            parameters: nil,
            completion: completion
        )
    }
}

// MARK: - Models

struct LeaderboardEntry: Codable {
    let userId: String
    let nickname: String
    let value: Double
    let rank: Int
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case nickname
        case value
        case rank
    }
}

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
    let message: String
}

struct Badge: Codable {
    let id: String
    let name: String
    let description: String
    let iconUrl: String?
    let earnedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id
        case name
        case description
        case iconUrl = "icon_url"
        case earnedAt = "earned_at"
    }
}
