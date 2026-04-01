import Foundation

class UserRepository {
    static let shared = UserRepository()
    
    private let apiService = APIService.shared
    private let cacheManager = CacheManager.shared
    
    private init() {}
    
    // MARK: - User Profile
    
    func getUserProfile(userId: String, forceRefresh: Bool = false, completion: @escaping (Result<User, Error>) -> Void) {
        // Try cache first if not forcing refresh
        if !forceRefresh, let cachedUser = cacheManager.getCachedUser(id: userId) {
            completion(.success(cachedUser))
            return
        }
        
        // Fetch from API
        apiService.getUserProfile(userId: userId) { [weak self] result in
            switch result {
            case .success(let user):
                // Cache the result
                self?.cacheManager.cacheUser(user)
                completion(.success(user))
                
            case .failure(let error):
                // If API fails, try to return cached data
                if let cachedUser = self?.cacheManager.getCachedUser(id: userId) {
                    completion(.success(cachedUser))
                } else {
                    completion(.failure(error))
                }
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
}
