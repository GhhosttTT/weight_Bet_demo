import Foundation
import Alamofire

class APIService {
    static let shared = APIService()
    
    private let baseURL: String
    private let session: Session
    
    private init() {
        // Read base URL from Info.plist for environment configuration; fallback to localhost
        if let info = Bundle.main.infoDictionary, let configured = info["API_BASE_URL"] as? String, !configured.isEmpty {
            baseURL = configured
        } else {
            baseURL = "http://localhost:8000/api" // TODO: Update with production URL
        }

        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 30
        configuration.timeoutIntervalForResource = 30
        
        // Combine auth and retry interceptors
        let authInterceptor = AuthInterceptor()
        let retryInterceptor = RetryInterceptor()
        let compositeInterceptor = Interceptor(adapters: [authInterceptor], retriers: [authInterceptor, retryInterceptor])
        
        // Add error monitoring
        let errorMonitor = ErrorInterceptor()
        
        session = Session(
            configuration: configuration,
            interceptor: compositeInterceptor,
            eventMonitors: [errorMonitor]
        )
    }
    
    // MARK: - Auth Endpoints
    
    func login(email: String, password: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let request = LoginRequest(email: email, password: password)
        
        session.request("\(baseURL)/auth/login",
                       method: .post,
                       parameters: request,
                       encoder: JSONParameterEncoder.default)
            .validate()
            .responseDecodable(of: APIResponse<AuthResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func register(email: String, password: String, nickname: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let request = RegisterRequest(email: email, password: password, nickname: nickname)
        
        session.request("\(baseURL)/auth/register",
                       method: .post,
                       parameters: request,
                       encoder: JSONParameterEncoder.default)
            .validate()
            .responseDecodable(of: APIResponse<AuthResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func refreshToken(refreshToken: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let parameters = ["refresh_token": refreshToken]
        
        session.request("\(baseURL)/auth/refresh",
                       method: .post,
                       parameters: parameters,
                       encoder: JSONParameterEncoder.default)
            .validate()
            .responseDecodable(of: APIResponse<AuthResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func googleLogin(idToken: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let parameters = ["id_token": idToken]
        
        session.request("\(baseURL)/auth/google",
                       method: .post,
                       parameters: parameters,
                       encoder: JSONParameterEncoder.default)
            .validate()
            .responseDecodable(of: APIResponse<AuthResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    // MARK: - User Endpoints
    
    func getUserProfile(userId: String, completion: @escaping (Result<User, Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)",
                       method: .get)
            .validate()
            .responseDecodable(of: APIResponse<User>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func updateUserProfile(userId: String, parameters: [String: Any], completion: @escaping (Result<User, Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)",
                       method: .put,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<User>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func bindPaymentMethod(userId: String, parameters: [String: Any], completion: @escaping (Result<Void, Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)/payment-methods",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }
    
    // MARK: - Betting Plan Endpoints
    
    func createBettingPlan(parameters: [String: Any], completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<BettingPlan>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getBettingPlan(planId: String, completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)",
                       method: .get)
            .validate()
            .responseDecodable(of: APIResponse<BettingPlan>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getUserBettingPlans(userId: String, status: String? = nil, completion: @escaping (Result<[BettingPlan], Error>) -> Void) {
        var parameters: [String: String] = [:]
        if let status = status {
            parameters["status"] = status
        }
        
        session.request("\(baseURL)/users/\(userId)/betting-plans",
                       method: .get,
                       parameters: parameters)
            .validate()
            .responseDecodable(of: APIResponse<[BettingPlan]>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func acceptBettingPlan(planId: String, parameters: [String: Any], completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/accept",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<BettingPlan>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func rejectBettingPlan(planId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/reject",
                       method: .post)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }
    
    func cancelBettingPlan(planId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/cancel",
                       method: .post)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }
    
    func inviteParticipant(planId: String, inviteeId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        let parameters = ["invitee_id": inviteeId]
        
        session.request("\(baseURL)/betting-plans/\(planId)/invite",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }
    
    // MARK: - Check-In Endpoints
    
    func createCheckIn(parameters: [String: Any], completion: @escaping (Result<CheckIn, Error>) -> Void) {
        session.request("\(baseURL)/check-ins",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<CheckIn>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getCheckInHistory(planId: String, userId: String? = nil, completion: @escaping (Result<[CheckIn], Error>) -> Void) {
        var parameters: [String: String] = [:]
        if let userId = userId {
            parameters["user_id"] = userId
        }
        
        session.request("\(baseURL)/betting-plans/\(planId)/check-ins",
                       method: .get,
                       parameters: parameters)
            .validate()
            .responseDecodable(of: APIResponse<[CheckIn]>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getProgress(planId: String, userId: String, completion: @escaping (Result<ProgressStats, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/progress",
                       method: .get,
                       parameters: ["user_id": userId])
            .validate()
            .responseDecodable(of: APIResponse<ProgressStats>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func uploadCheckInPhoto(checkInId: String, imageData: Data, completion: @escaping (Result<String, Error>) -> Void) {
        session.upload(
            multipartFormData: { multipartFormData in
                multipartFormData.append(imageData, withName: "photo", fileName: "checkin.jpg", mimeType: "image/jpeg")
            },
            to: "\(baseURL)/check-ins/\(checkInId)/photo"
        )
        .validate()
        .responseDecodable(of: APIResponse<PhotoUploadResponse>.self) { response in
            switch response.result {
            case .success(let apiResponse):
                if apiResponse.success, let data = apiResponse.data {
                    completion(.success(data.photoUrl))
                } else {
                    let error = NSError(domain: "APIError",
                                      code: -1,
                                      userInfo: [NSLocalizedDescriptionKey: apiResponse.error ?? "Photo upload failed"])
                    completion(.failure(error))
                }
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func reviewCheckIn(checkInId: String, approved: Bool, comment: String?, completion: @escaping (Result<Void, Error>) -> Void) {
        var parameters: [String: Any] = ["approved": approved]
        if let comment = comment {
            parameters["comment"] = comment
        }
        
        session.request("\(baseURL)/check-ins/\(checkInId)/review",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }
    
    // MARK: - Payment Endpoints
    
    func getBalance(userId: String, completion: @escaping (Result<Balance, Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)/balance",
                       method: .get)
            .validate()
            .responseDecodable(of: APIResponse<Balance>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getTransactionHistory(userId: String, completion: @escaping (Result<[Transaction], Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)/transactions",
                       method: .get)
            .validate()
            .responseDecodable(of: APIResponse<[Transaction]>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func charge(amount: Double, paymentMethodId: String, completion: @escaping (Result<ChargeResult, Error>) -> Void) {
        let parameters: [String: Any] = [
            "amount": amount,
            "payment_method_id": paymentMethodId
        ]
        
        session.request("\(baseURL)/payments/charge",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<ChargeResult>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func withdraw(amount: Double, completion: @escaping (Result<WithdrawResult, Error>) -> Void) {
        let parameters = ["amount": amount]
        
        session.request("\(baseURL)/payments/withdraw",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<WithdrawResult>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    // MARK: - Social Endpoints
    
    func getLeaderboard(type: String, limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        session.request("\(baseURL)/social/leaderboard/\(type)",
                       method: .get,
                       parameters: ["limit": limit])
            .validate()
            .responseDecodable(of: APIResponse<[LeaderboardEntry]>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func postComment(planId: String, content: String, completion: @escaping (Result<Comment, Error>) -> Void) {
        let parameters = ["content": content]
        
        session.request("\(baseURL)/social/betting-plans/\(planId)/comments",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: APIResponse<Comment>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getComments(planId: String, completion: @escaping (Result<[Comment], Error>) -> Void) {
        session.request("\(baseURL)/social/betting-plans/\(planId)/comments",
                       method: .get)
            .validate()
            .responseDecodable(of: APIResponse<[Comment]>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    func getUserBadges(userId: String, completion: @escaping (Result<[Badge], Error>) -> Void) {
        session.request("\(baseURL)/social/users/\(userId)/badges",
                       method: .get)
            .validate()
            .responseDecodable(of: APIResponse<[Badge]>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }
    
    // MARK: - Notification Endpoints
    
    func registerDeviceToken(token: String, completion: @escaping (Result<Void, Error>) -> Void) {
        let parameters = ["device_token": token, "platform": "ios"]
        
        session.request("\(baseURL)/notifications/register",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }

    // MARK: - Pending Actions Endpoints

    func getPendingActions(completion: @escaping (Result<PendingActionsResponse, Error>) -> Void) {
        session.request("\(baseURL)/me/pending-actions", method: .get)
            .validate()
            .responseDecodable(of: APIResponse<PendingActionsResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }

    func markInvitationSeen(invitationId: String, userId: String? = nil, completion: @escaping (Result<Void, Error>) -> Void) {
        var parameters: [String: Any] = [:]
        if let userId = userId {
            parameters["userId"] = userId
        }

        session.request("\(baseURL)/invitations/\(invitationId)/mark-seen",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }

    func postDoubleCheck(planId: String, parameters: [String: Any], completion: @escaping (Result<Void, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/doublecheck",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .response { response in
                if let error = response.error {
                    completion(.failure(error))
                } else {
                    completion(.success(()))
                }
            }
    }

    // MARK: - Recommendation Endpoints

    func getRecommendation(useCache: Bool = true, completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        var parameters: [String: String] = [:]
        if !useCache {
            parameters["use_cache"] = "false"
        }

        session.request("\(baseURL)/recommendations/",
                       method: .get,
                       parameters: parameters)
            .validate()
            .responseDecodable(of: APIResponse<RecommendationResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }

    func refreshRecommendation(completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        session.request("\(baseURL)/recommendations/refresh",
                       method: .post)
            .validate()
            .responseDecodable(of: APIResponse<RecommendationResponse>.self) { response in
                self.handleResponse(response, completion: completion)
            }
    }

    // MARK: - Helper Methods
    
    private func handleResponse<T: Codable>(_ response: AFDataResponse<APIResponse<T>>, completion: @escaping (Result<T, Error>) -> Void) {
        switch response.result {
        case .success(let apiResponse):
            if apiResponse.success, let data = apiResponse.data {
                completion(.success(data))
            } else {
                let errorMessage = apiResponse.error ?? apiResponse.message ?? "Unknown error"
                let error = self.parseError(from: response.response, message: errorMessage)
                completion(.failure(error))
            }
        case .failure(let afError):
            let error = self.handleAFError(afError, response: response.response)
            completion(.failure(error))
        }
    }
    
    private func parseError(from response: HTTPURLResponse?, message: String) -> NetworkError {
        guard let statusCode = response?.statusCode else {
            return .unknownError(message)
        }
        
        switch statusCode {
        case 401:
            return .unauthorizedError(message)
        case 400, 422:
            return .validationError(message)
        case 500...599:
            return .serverError(statusCode, message)
        default:
            return .unknownError(message)
        }
    }
    
    private func handleAFError(_ error: AFError, response: HTTPURLResponse?) -> NetworkError {
        if let underlyingError = error.underlyingError as? URLError {
            switch underlyingError.code {
            case .timedOut:
                return .timeoutError("Request timed out. Please check your network connection.")
            case .notConnectedToInternet, .networkConnectionLost:
                return .networkError("No internet connection. Please check your network settings.")
            default:
                return .networkError(underlyingError.localizedDescription)
            }
        }
        
        if let statusCode = response?.statusCode {
            switch statusCode {
            case 401:
                return .unauthorizedError("Unauthorized. Please login again.")
            case 400, 422:
                return .validationError("Invalid request data.")
            case 500...599:
                return .serverError(statusCode, "Server error occurred.")
            default:
                return .unknownError(error.localizedDescription)
            }
        }
        
        return .unknownError(error.localizedDescription)
    }
}

// MARK: - Supporting Models

struct PhotoUploadResponse: Codable {
    let photoUrl: String
    
    enum CodingKeys: String, CodingKey {
        case photoUrl = "photo_url"
    }
}

struct ChargeResult: Codable {
    let transactionId: String
    let amount: Double
    let status: String
    
    enum CodingKeys: String, CodingKey {
        case transactionId = "transaction_id"
        case amount, status
    }
}

struct WithdrawResult: Codable {
    let transactionId: String
    let amount: Double
    let status: String
    
    enum CodingKeys: String, CodingKey {
        case transactionId = "transaction_id"
        case amount, status
    }
}

struct LeaderboardEntry: Codable {
    let userId: String
    let nickname: String
    let value: Double
    let rank: Int
    
    enum CodingKeys: String, CodingKey {
        case userId = "user_id"
        case nickname, value, rank
    }
}

struct Comment: Codable {
    let id: String
    let userId: String
    let planId: String
    let content: String
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, content
        case userId = "user_id"
        case planId = "plan_id"
        case createdAt = "created_at"
    }
}

struct Badge: Codable {
    let id: String
    let name: String
    let description: String
    let iconUrl: String?
    let earnedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, name, description
        case iconUrl = "icon_url"
        case earnedAt = "earned_at"
    }
}

// Pending actions models
struct InvitationItem: Codable {
    let id: String
    let planId: String
    let fromUserId: String
    let message: String?
    let type: String?
    let isFirstTime: Bool?

    enum CodingKeys: String, CodingKey {
        case id
        case planId = "planId"
        case fromUserId = "fromUserId"
        case message
        case type
        case isFirstTime = "isFirstTime"
    }
}

struct DoubleCheckItem: Codable {
    let planId: String
    let initiatorId: String
    let reason: String?
    let isPending: Bool?

    enum CodingKeys: String, CodingKey {
        case planId = "planId"
        case initiatorId = "initiatorId"
        case reason
        case isPending = "isPending"
    }
}

struct PendingActionsResponse: Codable {
    let invitations: [InvitationItem]?
    let doubleChecks: [DoubleCheckItem]?
}
