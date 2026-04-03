import Foundation

class EditProfileViewModel {
    private let userRepository = UserRepository.shared
    
    // MARK: - Update Profile
    
    func updateProfile(
        userId: String,
        nickname: String,
        gender: Gender,
        age: Int,
        height: Double,
        currentWeight: Double,
        targetWeight: Double?,
        completion: @escaping (Result<User, Error>) -> Void
    ) {
        // Validate input
        guard nickname.count >= 2 else {
            completion(.failure(ValidationError.nicknameTooShort))
            return
        }
        
        guard age >= 13 && age <= 120 else {
            completion(.failure(ValidationError.invalidAge))
            return
        }
        
        guard height >= 100 && height <= 250 else {
            completion(.failure(ValidationError.invalidHeight))
            return
        }
        
        guard currentWeight >= 30 && currentWeight <= 300 else {
            completion(.failure(ValidationError.invalidWeight))
            return
        }
        
        if let targetWeight = targetWeight {
            guard targetWeight >= 30 && targetWeight <= 300 else {
                completion(.failure(ValidationError.invalidWeight))
                return
            }
        }
        
        // Build parameters
        var parameters: [String: Any] = [
            "nickname": nickname,
            "gender": gender.rawValue,
            "age": age,
            "height": height,
            "current_weight": currentWeight
        ]
        
        if let targetWeight = targetWeight {
            parameters["target_weight"] = targetWeight
        }
        
        // Update profile
        userRepository.updateUserProfile(userId: userId, parameters: parameters, completion: completion)
    }
}

// MARK: - Additional Validation Errors

extension ValidationError {
    static let invalidAge = ValidationError.custom("年龄必须在13-120岁之间")
    static let invalidHeight = ValidationError.custom("身高必须在100-250 cm之间")
    static let invalidWeight = ValidationError.custom("体重必须在30-300 kg之间")
}
