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
    static let invalidAge = ValidationError.custom("Age must be between 13 and 120")
    static let invalidHeight = ValidationError.custom("Height must be between 100 and 250 cm")
    static let invalidWeight = ValidationError.custom("Weight must be between 30 and 300 kg")
    
    case custom(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidEmail:
            return "Please enter a valid email address"
        case .passwordTooShort:
            return "Password must be at least 6 characters"
        case .passwordsDoNotMatch:
            return "Passwords do not match"
        case .nicknameTooShort:
            return "Nickname must be at least 2 characters"
        case .custom(let message):
            return message
        }
    }
}
