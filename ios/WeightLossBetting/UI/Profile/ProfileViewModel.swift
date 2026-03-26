import Foundation

class ProfileViewModel {
    private let authRepository = AuthRepository.shared
    private let userRepository = UserRepository.shared
    
    // MARK: - Load Profile
    
    func loadUserProfile(completion: @escaping (Result<User, Error>) -> Void) {
        guard let userId = authRepository.getCurrentUserId() else {
            completion(.failure(NSError(domain: "ProfileViewModel", code: -1, userInfo: [NSLocalizedDescriptionKey: "User not logged in"])))
            return
        }
        
        userRepository.getUserProfile(userId: userId, forceRefresh: false, completion: completion)
    }
    
    // MARK: - Logout
    
    func logout() {
        authRepository.logout()
    }
}
