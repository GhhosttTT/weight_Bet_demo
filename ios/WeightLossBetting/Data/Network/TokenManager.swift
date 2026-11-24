import Foundation
import KeychainAccess

class TokenManager {
    static let shared = TokenManager()
    
    private let keychain = Keychain(service: "com.weightloss.betting")
    private let accessTokenKey = "access_token"
    private let refreshTokenKey = "refresh_token"
    private let userIdKey = "user_id"
    private let pendingChargeKey = "pending_charge_transaction_id"
    
    private init() {}
    
    func saveTokens(accessToken: String, refreshToken: String) {
        do {
            try keychain.set(accessToken, key: accessTokenKey)
            try keychain.set(refreshToken, key: refreshTokenKey)
        } catch {
            print("Error saving tokens: \(error)")
        }
    }
    
    func saveUserId(_ userId: String) {
        do {
            try keychain.set(userId, key: userIdKey)
        } catch {
            print("Error saving user ID: \(error)")
        }
    }
    
    func getUserId() -> String? {
        return try? keychain.get(userIdKey)
    }

    func clearUserId() {
        do {
            try keychain.remove(userIdKey)
        } catch {
            print("Error clearing user ID: \(error)")
        }
    }

    func savePendingCharge(_ transactionId: String) {
        do {
            try keychain.set(transactionId, key: pendingChargeKey)
        } catch {
            print("Error saving pending charge: \(error)")
        }
    }

    func getPendingCharge() -> String? {
        return try? keychain.get(pendingChargeKey)
    }

    func clearPendingCharge() {
        do {
            try keychain.remove(pendingChargeKey)
        } catch {
            print("Error clearing pending charge: \(error)")
        }
    }
    
    func getAccessToken() -> String? {
        return try? keychain.get(accessTokenKey)
    }
    
    func getRefreshToken() -> String? {
        return try? keychain.get(refreshTokenKey)
    }
    
    func clearTokens() {
        do {
            try keychain.remove(accessTokenKey)
            try keychain.remove(refreshTokenKey)
            try keychain.remove(userIdKey)
            try keychain.remove(pendingChargeKey)
        } catch {
            print("Error clearing tokens: \(error)")
        }
    }
    
    func hasValidToken() -> Bool {
        return getAccessToken() != nil
    }
}
