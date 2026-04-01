import Foundation

// MARK: - User Model

struct User: Codable {
    let id: String
    let email: String
    let phoneNumber: String?
    let nickname: String
    let gender: Gender
    let age: Int
    let height: Double // cm
    let currentWeight: Double // kg
    let targetWeight: Double? // kg
    let paymentMethod: String?
    let createdAt: Date
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, email, nickname, gender, age, height
        case phoneNumber = "phone_number"
        case currentWeight = "current_weight"
        case targetWeight = "target_weight"
        case paymentMethod = "payment_method"
        case createdAt = "created_at"
        case updatedAt = "updated_at"
    }
}

enum Gender: String, Codable {
    case male
    case female
    case other
}

// MARK: - Betting Plan Model

struct BettingPlan: Codable {
    let id: String
    let creatorId: String
    let participantId: String?
    let status: PlanStatus
    let betAmount: Double
    let startDate: Date
    let endDate: Date
    let description: String?
    let creatorGoal: Goal
    let participantGoal: Goal?
    let createdAt: Date
    let activatedAt: Date?
    
    enum CodingKeys: String, CodingKey {
        case id, status, description
        case creatorId = "creator_id"
        case participantId = "participant_id"
        case betAmount = "bet_amount"
        case startDate = "start_date"
        case endDate = "end_date"
        case creatorGoal = "creator_goal"
        case participantGoal = "participant_goal"
        case createdAt = "created_at"
        case activatedAt = "activated_at"
    }
}

struct Goal: Codable {
    let initialWeight: Double
    let targetWeight: Double
    let targetWeightLoss: Double
    
    enum CodingKeys: String, CodingKey {
        case initialWeight = "initial_weight"
        case targetWeight = "target_weight"
        case targetWeightLoss = "target_weight_loss"
    }
}

enum PlanStatus: String, Codable {
    case pending
    case active
    case completed
    case cancelled
    case rejected
}

// MARK: - Badge Model

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

// MARK: - Check-In Model

struct CheckIn: Codable {
    let id: String
    let userId: String
    let planId: String
    let weight: Double
    let checkInDate: Date
    let photoUrl: String?
    let note: String?
    let reviewStatus: ReviewStatus
    let reviewerId: String?
    let reviewComment: String?
    let createdAt: Date
    
    enum CodingKeys: String, CodingKey {
        case id, weight, note
        case userId = "user_id"
        case planId = "plan_id"
        case checkInDate = "check_in_date"
        case photoUrl = "photo_url"
        case reviewStatus = "review_status"
        case reviewerId = "reviewer_id"
        case reviewComment = "review_comment"
        case createdAt = "created_at"
    }
}

enum ReviewStatus: String, Codable {
    case pending
    case approved
    case rejected
}

// MARK: - Progress Stats

struct ProgressStats: Codable {
    let currentWeight: Double
    let initialWeight: Double
    let targetWeight: Double
    let weightLoss: Double
    let targetWeightLoss: Double
    let progressPercentage: Double
    let checkInCount: Int
    let daysRemaining: Int
    
    enum CodingKeys: String, CodingKey {
        case checkInCount = "check_in_count"
        case currentWeight = "current_weight"
        case daysRemaining = "days_remaining"
        case initialWeight = "initial_weight"
        case progressPercentage = "progress_percentage"
        case targetWeight = "target_weight"
        case targetWeightLoss = "target_weight_loss"
        case weightLoss = "weight_loss"
    }
}

// MARK: - Balance

struct Balance: Codable {
    let availableBalance: Double
    let frozenBalance: Double
    let updatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case availableBalance = "available_balance"
        case frozenBalance = "frozen_balance"
        case updatedAt = "updated_at"
    }
}

// MARK: - Bank Account

struct BankAccount: Codable {
    let bankName: String
    let accountNumber: String
    let accountHolderName: String
    
    enum CodingKeys: String, CodingKey {
        case bankName = "bank_name"
        case accountNumber = "account_number"
        case accountHolderName = "account_holder_name"
    }
}

// MARK: - Transaction

struct Transaction: Codable {
    let id: String
    let userId: String
    let type: TransactionType
    let amount: Double
    let status: TransactionStatus
    let relatedPlanId: String?
    let relatedSettlementId: String?
    let createdAt: Date
    let completedAt: Date?
    
    enum CodingKeys: String, CodingKey {
        case id, type, amount, status
        case userId = "user_id"
        case relatedPlanId = "related_plan_id"
        case relatedSettlementId = "related_settlement_id"
        case createdAt = "created_at"
        case completedAt = "completed_at"
    }
}

enum TransactionType: String, Codable {
    case freeze
    case unfreeze
    case transfer
    case withdraw
    case refund
}

enum TransactionStatus: String, Codable {
    case pending
    case completed
    case failed
}

// MARK: - Auth Models

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct RegisterRequest: Codable {
    let email: String
    let password: String
    let nickname: String
}

struct AuthResponse: Codable {
    let accessToken: String
    let refreshToken: String
    let user: User
    
    enum CodingKeys: String, CodingKey {
        case user
        case accessToken = "access_token"
        case refreshToken = "refresh_token"
    }
}

// MARK: - API Response Wrapper

struct APIResponse<T: Codable>: Codable {
    let success: Bool
    let data: T?
    let message: String?
    let error: String?
}

// MARK: - Recommendation Models

struct ExerciseRecommendation: Codable {
    let type: String
    let duration: Int
    let intensity: String
    let description: String?
}

struct DietRecommendation: Codable {
    let mealType: String
    let foodItems: [String]
    let calories: Int?
    let tips: String?
    
    enum CodingKeys: String, CodingKey {
        case mealType = "meal_type"
        case foodItems = "food_items"
        case calories, tips
    }
}

struct RecommendationResponse: Codable {
    let success: Bool
    let exerciseRecommendations: [ExerciseRecommendation]
    let dietRecommendations: [DietRecommendation]
    let dailyCaloriesTarget: Int?
    let waterIntakeTarget: Int?
    let sleepTarget: Int?
    let tips: String?
    let generatedAt: Date
    
    enum CodingKeys: String, CodingKey {
        case success, tips
        case exerciseRecommendations = "exercise_recommendations"
        case dietRecommendations = "diet_recommendations"
        case dailyCaloriesTarget = "daily_calories_target"
        case waterIntakeTarget = "water_intake_target"
        case sleepTarget = "sleep_target"
        case generatedAt = "generated_at"
    }
}
