import Foundation

class AuthRepository {
    static let shared = AuthRepository()
    
    private lazy var apiService = APIService.shared // 懒加载，打破循环依赖
    private lazy var cacheManager = CacheManager.shared // 懒加载，打破循环依赖
    private let keychainManager = KeychainManager.shared
    
    private init() {}
    
    // MARK: - Authentication
    
    func login(email: String, password: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        apiService.login(email: email, password: password) { [weak self] result in
            switch result {
            case .success(let authResponse):
                // Save tokens to Keychain
                self?.keychainManager.saveAccessToken(authResponse.accessToken)
                self?.keychainManager.saveRefreshToken(authResponse.refreshToken)
                
                // Save user ID to UserDefaults
                UserDefaults.standard.set(authResponse.user.id, forKey: "currentUserId")
                
                // Cache user data
                self?.cacheManager.cacheUser(authResponse.user)
                
                completion(.success(authResponse))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func register(email: String, password: String, nickname: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        apiService.register(email: email, password: password, nickname: nickname) { [weak self] result in
            switch result {
            case .success(let authResponse):
                // Save tokens to Keychain
                self?.keychainManager.saveAccessToken(authResponse.accessToken)
                self?.keychainManager.saveRefreshToken(authResponse.refreshToken)
                
                // Save user ID to UserDefaults
                UserDefaults.standard.set(authResponse.user.id, forKey: "currentUserId")
                
                // Cache user data
                self?.cacheManager.cacheUser(authResponse.user)
                
                completion(.success(authResponse))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func googleLogin(idToken: String, completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        apiService.googleLogin(idToken: idToken) { [weak self] result in
            switch result {
            case .success(let authResponse):
                // Save tokens to Keychain
                self?.keychainManager.saveAccessToken(authResponse.accessToken)
                self?.keychainManager.saveRefreshToken(authResponse.refreshToken)
                
                // Save user ID to UserDefaults
                UserDefaults.standard.set(authResponse.user.id, forKey: "currentUserId")
                
                // Cache user data
                self?.cacheManager.cacheUser(authResponse.user)
                
                completion(.success(authResponse))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func refreshToken(completion: @escaping (Result<AuthResponse, Error>) -> Void) {
        guard let refreshToken = keychainManager.getRefreshToken() else {
            completion(.failure(NSError(domain: "AuthRepository", code: -1, userInfo: [NSLocalizedDescriptionKey: "No refresh token found"])))
            return
        }
        
        apiService.refreshToken(refreshToken: refreshToken) { [weak self] result in
            switch result {
            case .success(let authResponse):
                // Update tokens in Keychain
                self?.keychainManager.saveAccessToken(authResponse.accessToken)
                self?.keychainManager.saveRefreshToken(authResponse.refreshToken)
                
                // Update cached user data
                self?.cacheManager.cacheUser(authResponse.user)
                
                completion(.success(authResponse))
                
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
    
    func logout() {
        // Clear tokens from Keychain
        keychainManager.deleteAccessToken()
        keychainManager.deleteRefreshToken()
        
        // Clear user ID from UserDefaults
        UserDefaults.standard.removeObject(forKey: "currentUserId")
        
        // Clear all cached data
        cacheManager.invalidateAllCache()
    }
    
    // MARK: - Token Management
    
    func getAccessToken() -> String? {
        return keychainManager.getAccessToken()
    }
    
    func getRefreshToken() -> String? {
        return keychainManager.getRefreshToken()
    }
    
    func isLoggedIn() -> Bool {
        return keychainManager.getAccessToken() != nil
    }
    
    func getCurrentUserId() -> String? {
        return UserDefaults.standard.string(forKey: "currentUserId")
    }
}
