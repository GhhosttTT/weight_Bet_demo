import Foundation
import UIKit

class LoginViewModel {
    private let authRepository = AuthRepository.shared

    func login(email: String, password: String, completion: @escaping (Result<Void, Error>) -> Void) {
        authRepository.login(email: email, password: password) { result in
            switch result {
            case .success(_):
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    // Google Sign-In functionality is temporarily disabled due to dependency issues
    func googleSignIn(presentingViewController: UIViewController, completion: @escaping (Result<Void, Error>) -> Void) {
        let error = NSError(domain: "LoginViewModel", code: -1, userInfo: [NSLocalizedDescriptionKey: "Google Sign-In is temporarily unavailable"])
        completion(.failure(error))
    }
}
