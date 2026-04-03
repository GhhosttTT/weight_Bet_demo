import Foundation
import UIKit

class LoginViewModel {
    private let authRepository = AuthRepository.shared
    private let recommendationRepository = RecommendationRepository.shared

    func login(email: String, password: String, completion: @escaping (Result<Void, Error>) -> Void) {
        authRepository.login(email: email, password: password) { [weak self] result in
            switch result {
            case .success(_):
                // Login successful, preload recommendation in background
                self?.preloadRecommendation()
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    /// Preload recommendation after login
    private func preloadRecommendation() {
        print("🔵 [LoginVM] Preloading recommendation after login...")
        recommendationRepository.preloadRecommendation()
    }

    // Google Sign-In functionality is temporarily disabled due to dependency issues
    func googleSignIn(presentingViewController: UIViewController, completion: @escaping (Result<Void, Error>) -> Void) {
        let error = NSError(domain: "LoginViewModel", code: -1, userInfo: [NSLocalizedDescriptionKey: "Google Sign-In is temporarily unavailable"])
        completion(.failure(error))
    }
}
