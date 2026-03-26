import Foundation
import UIKit
import GoogleSignIn

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

    func googleSignIn(presentingViewController: UIViewController, completion: @escaping (Result<Void, Error>) -> Void) {
        GIDSignIn.sharedInstance.signIn(withPresenting: presentingViewController) { signInResult, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let signInResult = signInResult,
                  let idToken = signInResult.user.idToken?.tokenString else {
                let error = NSError(domain: "LoginViewModel", code: -1, userInfo: [NSLocalizedDescriptionKey: "Failed to get Google ID token"])
                completion(.failure(error))
                return
            }

            // Call the backend with the ID token
            self.authRepository.googleLogin(idToken: idToken) { result in
                switch result {
                case .success(_):
                    completion(.success(()))
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        }
    }
}
