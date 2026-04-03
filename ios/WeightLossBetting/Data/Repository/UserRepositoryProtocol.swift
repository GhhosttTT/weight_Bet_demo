import Foundation

/// Protocol for user repository - used for dependency injection and testing
public protocol UserRepositoryProtocol {
    func getUserProfile(userId: String, completion: @escaping (Result<User, Error>) -> Void)
    func updateUserProfile(userId: String, updateData: UserUpdateRequest, completion: @escaping (Result<User, Error>) -> Void)
}

/// Request object for updating user profile
public struct UserUpdateRequest: Codable {
    let nickname: String
    let gender: Gender
    let age: Int
    let height: Double
    let currentWeight: Double
    let targetWeight: Double?
    
    enum CodingKeys: String, CodingKey {
        case nickname, gender, age, height
        case currentWeight = "current_weight"
        case targetWeight = "target_weight"
    }
    
    /// Validation
    func validate() -> Result<UserUpdateRequest, ValidationError> {
        // Validate nickname
        guard nickname.count >= 2 && nickname.count <= 50 else {
            return .failure(.nicknameTooShort)
        }
        
        // Validate age
        guard age >= 13 && age <= 120 else {
            return .failure(.invalidAge)
        }
        
        // Validate height
        guard height >= 100.0 && height <= 250.0 else {
            return .failure(.invalidHeight)
        }
        
        // Validate current weight
        guard currentWeight >= 30.0 && currentWeight <= 300.0 else {
            return .failure(.invalidWeight)
        }
        
        // Validate target weight if provided
        if let targetWeight = targetWeight {
            guard targetWeight >= 30.0 && targetWeight <= 300.0 else {
                return .failure(.invalidWeight)
            }
        }
        
        return .success(self)
    }
}
