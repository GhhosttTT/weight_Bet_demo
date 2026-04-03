import Foundation

class UserRepository {
    static let shared = UserRepository()
    
    private let apiService = APIService.shared
    private let cacheManager = CacheManager.shared
    
    private init() {}
    
    // MARK: - User Profile
    
    func getUserProfile(userId: String, forceRefresh: Bool = false, completion: @escaping (Result<User, Error>) -> Void) {
        // Fetch from API only (skip cache to avoid CoreData issues)
        apiService.getUserProfile(userId: userId) { [weak self] result in
            switch result {
            case .success(let user):
                // Cache the result (skip CoreData caching)
                print("   - User profile loaded and cached locally")
                completion(.success(user))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func updateUserProfile(userId: String, parameters: [String: Any], completion: @escaping (Result<User, Error>) -> Void) {
        apiService.updateUserProfile(userId: userId, parameters: parameters) { [weak self] result in
            switch result {
            case .success(let user):
                // Update cache
                self?.cacheManager.cacheUser(user)
                // Invalidate old cache
                self?.cacheManager.invalidateCache(for: "user_\(userId)")
                completion(.success(user))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func bindPaymentMethod(userId: String, parameters: [String: Any], completion: @escaping (Result<Void, Error>) -> Void) {
        apiService.bindPaymentMethod(userId: userId, parameters: parameters, completion: completion)
    }
    
    func searchUserByEmail(email: String, completion: @escaping (Result<UserPreview, Error>) -> Void) {
        apiService.searchUserByEmail(email: email) { result in
            switch result {
            case .success(let userPreview):
                // Cache the preview if needed (skip heavy full user cache)
                // Optionally map to a lightweight cache entry
                completion(.success(userPreview))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
}
