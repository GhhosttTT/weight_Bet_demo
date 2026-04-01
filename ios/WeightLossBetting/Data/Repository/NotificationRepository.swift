import Foundation

class NotificationRepository: BaseRepository {
    private lazy var apiService = APIService.shared
    
    func registerDeviceToken(token: String) async -> NetworkResult<Void> {
        return await safeApiCall { completion in
            self.apiService.registerDeviceToken(token: token, completion: completion)
        }
    }
}
