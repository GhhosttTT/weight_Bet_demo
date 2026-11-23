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

        guard nickname.count <= 20 else {
            completion(.failure(ValidationError.custom("昵称长度应在 2-20 个字符之间")))
            return
        }
        
        guard password.count >= 8 else {
            completion(.failure(ValidationError.passwordTooShort))
            return
        }

        guard age >= 13 && age <= 120 else {
            completion(.failure(ValidationError.custom("年龄应在 13-120 之间")))
            return
        }

        guard height.isFinite && height >= 100 && height <= 250 else {
            completion(.failure(ValidationError.custom("身高应在 100-250 cm 之间")))
            return
        }

        guard currentWeight.isFinite && currentWeight >= 30 && currentWeight <= 300 else {
            completion(.failure(ValidationError.custom("体重应在 30-300 kg 之间")))
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
