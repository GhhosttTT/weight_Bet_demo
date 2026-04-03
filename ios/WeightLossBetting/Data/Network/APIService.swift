import Foundation
import Alamofire

class APIService {
    static let shared = APIService()
    
    private let baseURL: String
    private let session: Session
    private let decoder: JSONDecoder
    
    private init() {
        // Read base URL from Info.plist for environment configuration
        if let info = Bundle.main.infoDictionary, let configured = info["API_BASE_URL"] as? String, !configured.isEmpty {
            baseURL = configured
        } else {
            // 本地后端服务 - 使用 Mac 的实际 IP 地址
            // iOS 模拟器无法使用 localhost，必须使用 Mac 的局域网 IP
            baseURL = "http://192.168.1.108:8000/api"
        }

        let configuration = URLSessionConfiguration.default
        configuration.timeoutIntervalForRequest = 60  // 增加请求超时时间
        configuration.timeoutIntervalForResource = 120  // 增加资源超时时间
        configuration.waitsForConnectivity = false  // 不等待网络连接
        
        // Combine auth and retry interceptors
        let authInterceptor = AuthInterceptor()
        let retryInterceptor = RetryInterceptor()
        let compositeInterceptor = Interceptor(adapters: [authInterceptor], retriers: [authInterceptor, retryInterceptor])
        
        // Add error monitoring
        let errorMonitor = ErrorInterceptor()

        // Configure the JSON decoder for date parsing
        let decoder = JSONDecoder()
        // Use custom date decoding strategy to handle multiple formats
        decoder.dateDecodingStrategy = .custom { decoder in
            let container = try decoder.singleValueContainer()
            let dateString = try container.decode(String.self)
            
            // Try ISO8601 first (most common)
            let iso8601Formatter = ISO8601DateFormatter()
            iso8601Formatter.formatOptions = [.withInternetDateTime, .withFractionalSeconds]
            if let date = iso8601Formatter.date(from: dateString) {
                return date
            }
            
            // Try without fractional seconds
            iso8601Formatter.formatOptions = [.withInternetDateTime]
            if let date = iso8601Formatter.date(from: dateString) {
                return date
            }
            
            // Fallback to DateFormatter for other formats
            let dateFormatter = DateFormatter()
            dateFormatter.locale = Locale(identifier: "en_US_POSIX")
            dateFormatter.timeZone = TimeZone(secondsFromGMT: 0)
            
            // Common date formats
            let formats = [
                "yyyy-MM-dd'T'HH:mm:ss.SSSSSS",
                "yyyy-MM-dd'T'HH:mm:ss.SSS",
                "yyyy-MM-dd'T'HH:mm:ss",
                "yyyy-MM-dd HH:mm:ss",
                "yyyy-MM-dd"
            ]
            
            for format in formats {
                dateFormatter.dateFormat = format
                if let date = dateFormatter.date(from: dateString) {
                    return date
                }
            }
            
            // If all else fails, throw error
            throw DecodingError.dataCorruptedError(in: container, debugDescription: "Cannot decode date string \(dateString)")
        }
        decoder.nonConformingFloatDecodingStrategy = .convertFromString(positiveInfinity: "Inf", negativeInfinity: "-Inf", nan: "NaN")
        self.decoder = decoder
        
        session = Session(
            configuration: configuration,
            interceptor: compositeInterceptor,
            eventMonitors: [errorMonitor]
        )
        
        // Print base URL for debugging
        print("🔧 APIService baseURL: \(baseURL)")
    }
    
    // MARK: - Auth Endpoints
    
    func login(email: String, password: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let request = LoginRequest(email: email, password: password)

        session.request("\(baseURL)/auth/login",
                       method: .post,
                       parameters: request,
                       encoder: JSONParameterEncoder.default,
                       headers: ["Content-Type": "application/json"])
            .validate()
            .responseDecodable(of: AuthResponse.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func register(email: String, password: String, nickname: String, gender: Gender, age: Int, height: Double, currentWeight: Double, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let request = RegisterRequest(
            email: email,
            password: password,
            nickname: nickname,
            gender: gender.rawValue,
            age: age,
            height: height,
            currentWeight: currentWeight
        )
        
        session.request("\(baseURL)/auth/register",
                       method: .post,
                       parameters: request,
                       encoder: JSONParameterEncoder.json)
            .validate()
            .responseDecodable(of: AuthResponse.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func refreshToken(refreshToken: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let parameters = ["refresh_token": refreshToken]
        
        session.request("\(baseURL)/auth/refresh",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: AuthResponse.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func googleLogin(idToken: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        let parameters = ["id_token": idToken]
        
        session.request("\(baseURL)/auth/google",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: AuthResponse.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    // MARK: - Generic Request Method
    func request<T: Codable>(
        endpoint: String,
        method: HTTPMethod = .get,
        parameters: [String: Any]? = nil,
        encoding: ParameterEncoding = URLEncoding.default,
        headers: HTTPHeaders? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        let url = "\(baseURL)\(endpoint)"
        
        session.request(
            url,
            method: method,
            parameters: parameters,
            encoding: encoding,
            headers: headers
        )
        .validate()
        .responseDecodable(of: APIResponse<T>.self) { response in
            self.handleResponse(response, completion: completion)
        }
    }
    
    // MARK: - User Endpoints
    
    func getUserProfile(userId: String, completion: @escaping (Result<User, Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)",
                       method: .get)
            .validate()
            .responseDecodable(of: User.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func updateUserProfile(userId: String, parameters: [String: Any], completion: @escaping (Result<User, Error>) -> Void) {
        session.request("\(baseURL)/users/\(userId)",
                       method: .put,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: User.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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
    
    func searchUserByEmail(email: String, completion: @escaping (Result<UserPreview, Error>) -> Void) {
        let url = "\(baseURL)/users/search?email=\(email.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? "")"
        print("🔍 [APIService] Searching user by email: \(url)")

        session.request(url, method: .get)
            .validate()
            .responseData { response in
                print("🔍 [APIService] Search response status: \(response.response?.statusCode ?? -1)")
                if let data = response.data,
                   let jsonString = String(data: data, encoding: .utf8) {
                    print("🔍 [APIService] Raw response: \(jsonString)")
                }

                guard let data = response.data else {
                    completion(.failure(response.error ?? NSError(domain: "APIService", code: -1, userInfo: [NSLocalizedDescriptionKey: "No data received"])))
                    return
                }

                // 1. Try APIResponse<UserPreview>
                if let apiResponse = try? self.decoder.decode(APIResponse<UserPreview>.self, from: data), apiResponse.success, let user = apiResponse.data {
                    completion(.success(user))
                    return
                }

                // 2. Try plain UserPreview
                if let user = try? self.decoder.decode(UserPreview.self, from: data) {
                    completion(.success(user))
                    return
                }

                // 3. Fallback: error
                let errorMessage: String
                if let apiResponse = try? self.decoder.decode(APIResponse<UserPreview>.self, from: data) {
                    errorMessage = apiResponse.error ?? apiResponse.message ?? "Unknown error"
                } else {
                    errorMessage = "Failed to decode user info"
                }
                let error = NSError(domain: "APIService", code: -1, userInfo: [NSLocalizedDescriptionKey: errorMessage])
                completion(.failure(error))
            }
    }
    
    // MARK: - Betting Plan Endpoints
    
    func createBettingPlan(parameters: [String: Any], completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        // 打印请求参数
        print("📡 [APIService] 创建计划请求参数:")
        for (key, value) in parameters {
            print("   - \(key): \(value)")
        }
        
        session.request("\(baseURL)/betting-plans",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: BettingPlan.self, decoder: decoder) { response in
                // 打印响应
                if let httpResponse = response.response {
                    print("📡 [APIService] 创建计划响应状态码：\(httpResponse.statusCode)")
                }
                if let responseData = response.data,
                   let jsonString = String(data: responseData, encoding: .utf8) {
                    print("📡 [APIService] 创建计划响应内容：\(jsonString)")
                }
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getBettingPlan(planId: String, completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)",
                       method: .get)
            .validate()
            .responseDecodable(of: BettingPlan.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getUserBettingPlans(userId: String, status: String? = nil, completion: @escaping (Result<[BettingPlan], Error>) -> Void) {
        var parameters: [String: String] = [:]
        if let status = status {
            parameters["status"] = status
        }
        
        // Try without /api prefix since betting-plans router might be registered at root
        session.request("\(baseURL)/betting-plans/users/\(userId)/plans",
                       method: .get,
                       parameters: parameters)
            .validate()
            .responseDecodable(of: [BettingPlan].self, decoder: decoder) { [weak self] response in
                guard let self = self else { return }
                
                // If 404, try fallback to alternative path
                if let httpError = response.error as? AFError,
                   httpError.responseCode == 404 {
                    print("⚠️ First endpoint failed, trying fallback...")
                    self.session.request("\(self.baseURL)/users/\(userId)/plans",
                                   method: .get,
                                   parameters: parameters)
                        .validate()
                        .responseDecodable(of: [BettingPlan].self, decoder: decoder) { fallbackResponse in
                            self.handleDirectResponse(fallbackResponse, completion: completion)
                        }
                } else {
                    self.handleDirectResponse(response, completion: completion)
                }
            }
    }
    
    func acceptBettingPlan(planId: String, parameters: [String: Any], completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/accept",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: BettingPlan.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func confirmBettingPlan(planId: String, completion: @escaping (Result<BettingPlan, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/confirm",
                       method: .post)
            .validate()
            .responseDecodable(of: BettingPlan.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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
    
    func giveUpBettingPlan(planId: String, completion: @escaping (Result<Void, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/give-up",
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
    
    func inviteParticipant(planId: String, inviteeEmail: String, completion: @escaping (Result<Invitation, Error>) -> Void) {
        let parameters = ["invitee_email": inviteeEmail]
        
        session.request("\(baseURL)/betting-plans/\(planId)/invite",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: Invitation.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    // MARK: - Invitation Endpoints
    
    func getInvitations(status: String? = nil, completion: @escaping (Result<[Invitation], Error>) -> Void) {
        var parameters: [String: Any] = [:]
        if let status = status {
            parameters["status"] = status
        }
        
        session.request("\(baseURL)/invitations",
                       method: .get,
                       parameters: parameters)
            .validate()
            .responseDecodable(of: [Invitation].self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getInvitationDetails(invitationId: String, completion: @escaping (Result<Invitation, Error>) -> Void) {
        session.request("\(baseURL)/invitations/\(invitationId)",
                       method: .get)
            .validate()
            .responseDecodable(of: Invitation.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func markInvitationViewed(invitationId: String, completion: @escaping (Result<Invitation, Error>) -> Void) {
        session.request("\(baseURL)/invitations/\(invitationId)/view",
                       method: .post)
            .validate()
            .responseDecodable(of: Invitation.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    // MARK: - Abandon Plan Endpoint
    
    func abandonPlan(planId: String, confirmation: Bool, completion: @escaping (Result<AbandonPlanResult, Error>) -> Void) {
        let parameters = ["confirmation": confirmation]
        
        session.request("\(baseURL)/betting-plans/\(planId)/abandon",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: AbandonPlanResult.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    // MARK: - Check-In Endpoints
    
    func createCheckIn(parameters: [String: Any], completion: @escaping (Result<CheckIn, Error>) -> Void) {
        session.request("\(baseURL)/check-ins",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: CheckIn.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getCheckInHistory(planId: String, userId: String? = nil, completion: @escaping (Result<[CheckIn], Error>) -> Void) {
        // Use the correct backend endpoint format
        guard let userId = userId else {
            completion(.failure(NSError(domain: "APIError", code: -1, userInfo: [NSLocalizedDescriptionKey: "User ID is required"])))
            return
        }
        
        session.request("\(baseURL)/check-ins/plan/\(planId)/user/\(userId)",
                       method: .get)
            .validate()
            .responseDecodable(of: [CheckIn].self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getProgress(planId: String, userId: String, completion: @escaping (Result<ProgressStats, Error>) -> Void) {
        session.request("\(baseURL)/betting-plans/\(planId)/progress",
                       method: .get,
                       parameters: ["user_id": userId])
            .validate()
            .responseDecodable(of: ProgressStats.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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
        .responseDecodable(of: APIResponse<PhotoUploadResponse>.self, decoder: decoder) { response in
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
        // Backend route is: /api/payments/users/{user_id}/balance
        session.request("\(baseURL)/payments/users/\(userId)/balance",
                       method: .get)
            .validate()
            .responseDecodable(of: Balance.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getTransactionHistory(userId: String, completion: @escaping (Result<[Transaction], Error>) -> Void) {
        // Backend route is: /api/payments/users/{user_id}/transactions
        session.request("\(baseURL)/payments/users/\(userId)/transactions",
                       method: .get)
            .validate()
            .responseDecodable(of: [Transaction].self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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
            .responseDecodable(of: ChargeResult.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func withdraw(amount: Double, completion: @escaping (Result<WithdrawResult, Error>) -> Void) {
        let parameters = ["amount": amount]
        
        session.request("\(baseURL)/payments/withdraw",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: WithdrawResult.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    // MARK: - Social Endpoints
    
    func getLeaderboard(type: String, limit: Int = 100, completion: @escaping (Result<[LeaderboardEntry], Error>) -> Void) {
        session.request("\(baseURL)/social/leaderboard/\(type)",
                       method: .get,
                       parameters: ["limit": limit])
            .validate()
            .responseDecodable(of: [LeaderboardEntry].self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func postComment(planId: String, content: String, completion: @escaping (Result<Comment, Error>) -> Void) {
        let parameters = ["content": content]
        
        session.request("\(baseURL)/social/betting-plans/\(planId)/comments",
                       method: .post,
                       parameters: parameters,
                       encoding: JSONEncoding.default)
            .validate()
            .responseDecodable(of: Comment.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getComments(planId: String, completion: @escaping (Result<[Comment], Error>) -> Void) {
        session.request("\(baseURL)/social/betting-plans/\(planId)/comments",
                       method: .get)
            .validate()
            .responseDecodable(of: [Comment].self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func getUserBadges(userId: String, completion: @escaping (Result<[Badge], Error>) -> Void) {
        session.request("\(baseURL)/social/users/\(userId)/badges",
                       method: .get)
            .validate()
            .responseDecodable(of: [Badge].self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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
            .responseDecodable(of: PendingActionsResponse.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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

        print("🔵 [APIService] Fetching recommendations from: \(baseURL)/recommendations/")
        session.request("\(baseURL)/recommendations/",
                       method: .get,
                       parameters: parameters)
            .validate()
            .responseDecodable(of: RecommendationResponse.self, decoder: decoder) { response in
                switch response.result {
                case .success:
                    print("✅ [APIService] Recommendations decoded successfully")
                case .failure(let error):
                    print("❌ [APIService] Failed to decode recommendations: \(error.localizedDescription)")
                    if let data = response.data,
                       let jsonString = String(data: data, encoding: .utf8) {
                        print("   Raw response: \(jsonString)")
                    }
                }
                self.handleDirectResponse(response, completion: completion)
            }
    }
    
    func refreshRecommendation(completion: @escaping (Result<RecommendationResponse, Error>) -> Void) {
        session.request("\(baseURL)/recommendations/refresh",
                       method: .post)
            .validate()
            .responseDecodable(of: RecommendationResponse.self, decoder: decoder) { response in
                self.handleDirectResponse(response, completion: completion)
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
        case 402:
            // Payment Required - Insufficient balance
            return .serverError(statusCode, message)
        case 400, 422:
            return .validationError(message)
        case 502:
            // Bad Gateway - 后端服务器问题
            return .serverError(statusCode, message)
        case 503:
            // Service Unavailable
            return .serverError(statusCode, "服务暂时不可用，请稍后再试")
        case 504:
            // Gateway Timeout
            return .timeoutError("服务器响应超时，请检查网络连接")
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
            case 402:
                // Payment Required - Insufficient balance
                return .serverError(statusCode, error.localizedDescription)
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
    
    // MARK: - Helper Methods for Direct Response (no APIResponse wrapper)
    
    private func handleDirectResponse<T: Codable>(_ response: DataResponse<T, AFError>, completion: @escaping (Result<T, Error>) -> Void) {
        switch response.result {
        case .success(let value):
            completion(.success(value))
        case .failure(let error):
            // 打印详细的错误信息用于调试
            print("❌ Error Response:")
            print("   URL: \(response.request?.url?.absoluteString ?? "unknown")")
            print("   Status Code: \(response.response?.statusCode ?? -1)")
            if let data = response.data, let responseString = String(data: data, encoding: .utf8) {
                print("   Response Body: \(responseString)")
            }
            print("   Error: \(error.localizedDescription)")
            
            if let statusCode = response.response?.statusCode {
                // Try to parse error message from response body
                var errorMessage = "HTTP \(statusCode): \(error.localizedDescription)"
                
                // 针对 502 错误提供更友好的提示
                if statusCode == 502 {
                    errorMessage = "服务器暂时无法访问，请检查：\n1. 后端服务是否正在运行\n2. 网络连接是否正常\n3. 服务器地址是否正确 (\(baseURL))"
                }
                
                if let data = response.data,
                   let errorResponse = try? JSONDecoder().decode(ErrorResponse.self, from: data),
                   let message = errorResponse.message ?? errorResponse.detail ?? errorResponse.error {
                    errorMessage = message
                }
                
                let networkError = parseError(from: response.response, message: errorMessage)
                completion(.failure(networkError))
            } else {
                let networkError = handleAFError(error, response: response.response)
                completion(.failure(networkError))
            }
        }
    }
}

