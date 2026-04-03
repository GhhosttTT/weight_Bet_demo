import Foundation

class RegisterViewModel {
    private let authRepository = AuthRepository.shared
    
    // MARK: - Register
    
    func register(email: String, password: String, nickname: String, gender: Gender, age: Int, height: Double, currentWeight: Double, completion: @escaping (Result<User, Error>) -> Void) {
        // Validate input
        guard isValidEmail(email) else {
            completion(.failure(ValidationError.invalidEmail))
            return
        }
        
        guard nickname.count >= 2 else {
            completion(.failure(ValidationError.nicknameTooShort))
            return
        }
        
        guard password.count >= 6 else {
            completion(.failure(ValidationError.passwordTooShort))
            return
        }
        
        // Perform registration
        authRepository.register(email: email, password: password, nickname: nickname, gender: gender, age: age, height: height, currentWeight: currentWeight) { result in
            switch result {
            case .success(let authResponse):
                // Create user from auth response with provided profile data
                let user = User(
                    id: authResponse.userId,
                    email: authResponse.email,
                    nickname: authResponse.nickname,
                    gender: gender,
                    age: age,
                    height: height,
                    currentWeight: currentWeight,
                    targetWeight: nil,
                    paymentMethod: nil,
                    createdAt: Date(),
                    updatedAt: Date()
                )
                completion(.success(user))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    // MARK: - Validation
    
    private func isValidEmail(_ email: String) -> Bool {
        let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        return emailPredicate.evaluate(with: email)
    }
}
