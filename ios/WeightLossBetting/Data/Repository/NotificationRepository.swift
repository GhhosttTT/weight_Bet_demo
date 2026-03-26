import Foundation

class NotificationRepository: BaseRepository {
    private let apiService = APIService.shared
    
    func registerDeviceToken(token: String) async -> NetworkResult<Void> {
        return await safeApiCall { completion in
            self.apiService.registerDeviceToken(token: token, completion: completion)
        }
    }
}
