import Foundation
import UIKit
import GoogleSignIn

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

    func googleSignIn(presentingViewController: UIViewController, completion: @escaping (Result<Void, Error>) -> Void) {
        guard let configuration = GIDSignIn.sharedInstance.configuration,
              !configuration.clientID.isEmpty else {
            let configurationError = NSError(
                domain: "LoginViewModel",
                code: -3,
                userInfo: [NSLocalizedDescriptionKey: "Google 登录尚未配置，请联系管理员"]
            )
            completion(.failure(configurationError))
            return
        }
        GIDSignIn.sharedInstance.signIn(withPresenting: presentingViewController) { [weak self] result, error in
            if let error = error {
                completion(.failure(error))
                return
            }
            guard let idToken = result?.user.idToken?.tokenString else {
                let tokenError = NSError(
                    domain: "LoginViewModel",
                    code: -2,
                    userInfo: [NSLocalizedDescriptionKey: "Google 未返回有效身份凭证"]
                )
                completion(.failure(tokenError))
                return
            }
            self?.authRepository.googleLogin(idToken: idToken) { authResult in
                switch authResult {
                case .success:
                    self?.preloadRecommendation()
                    completion(.success(()))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
}
