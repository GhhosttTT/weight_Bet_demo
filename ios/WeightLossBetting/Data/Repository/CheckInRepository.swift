import Foundation

class CheckInRepository {
    static let shared = CheckInRepository()
    
    private let apiService = APIService.shared
    private let cacheManager = CacheManager.shared
    private let offlineSyncManager = OfflineSyncManager.shared
    
    private init() {}
    
    // MARK: - Check-In Operations
    
    func createCheckIn(planId: String, weight: Double, note: String?, photoUrl: String?, completion: @escaping (Result<CheckIn, Error>) -> Void) {
        guard let userId = UserDefaults.standard.string(forKey: "currentUserId") else {
            completion(.failure(NSError(domain: "CheckInRepository", code: -1, userInfo: [NSLocalizedDescriptionKey: "User not logged in"])))
            return
        }
        
        // Format date as yyyy-MM-dd (exact date, no time)
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd"
        dateFormatter.timeZone = TimeZone.current
        
        var parameters: [String: Any] = [
            "user_id": userId,
            "plan_id": planId,
            "weight": weight,
            "check_in_date": dateFormatter.string(from: Date())
        ]
        
        if let note = note {
            parameters["note"] = note
        }
        
        if let photoUrl = photoUrl {
            parameters["photo_url"] = photoUrl
        }
        
        // Check if online
        if offlineSyncManager.isNetworkAvailable() {
            // Create check-in online
            apiService.createCheckIn(parameters: parameters) { [weak self] result in
                switch result {
                case .success(let checkIn):
                    // Cache the check-in
                    self?.cacheManager.cacheCheckIn(checkIn)
                    // Invalidate check-ins cache for this plan
                    self?.cacheManager.invalidateCache(for: "checkins_\(planId)")
                    completion(.success(checkIn))
                    
                case .failure(let error):
                    completion(.failure(error))
                }
            }
        } else {
            // Save to offline queue
            offlineSyncManager.saveOfflineCheckIn(
                planId: planId,
                weight: weight,
                note: note,
                photoUrl: photoUrl
            )
            
            // Create a temporary check-in object for UI
            let tempCheckIn = CheckIn(
                id: UUID().uuidString,
                userId: userId,
                planId: planId,
                weight: weight,
                checkInDate: Date(),
                photoUrl: photoUrl,
                note: note,
                reviewStatus: .pending,
                reviewerId: nil,
                reviewComment: nil,
                createdAt: Date()
            )
            
            completion(.success(tempCheckIn))
        }
    }
    
    func getCheckInHistory(planId: String, userId: String? = nil, forceRefresh: Bool = false, completion: @escaping (Result<[CheckIn], Error>) -> Void) {
        // Try cache first if not forcing refresh
        if !forceRefresh, let cachedCheckIns = cacheManager.getCachedCheckIns(planId: planId) {
            let filteredCheckIns = userId != nil ? cachedCheckIns.filter { $0.userId == userId } : cachedCheckIns
            completion(.success(filteredCheckIns))
            return
        }
        
        // Fetch from API
        apiService.getCheckInHistory(planId: planId, userId: userId) { [weak self] result in
            switch result {
            case .success(let checkIns):
                // Cache the results
                self?.cacheManager.cacheCheckIns(checkIns, planId: planId)
                completion(.success(checkIns))
                
            case .failure(let error):
                // If API fails, try to return cached data
                if let cachedCheckIns = self?.cacheManager.getCachedCheckIns(planId: planId) {
                    let filteredCheckIns = userId != nil ? cachedCheckIns.filter { $0.userId == userId } : cachedCheckIns
                    completion(.success(filteredCheckIns))
                } else {
                    completion(.failure(error))
                }
            }
        }
    }
    
    func getProgress(planId: String, userId: String, completion: @escaping (Result<ProgressStats, Error>) -> Void) {
        apiService.getProgress(planId: planId, userId: userId, completion: completion)
    }
    
    func uploadCheckInPhoto(checkInId: String, imageData: Data, completion: @escaping (Result<String, Error>) -> Void) {
        apiService.uploadCheckInPhoto(checkInId: checkInId, imageData: imageData, completion: completion)
    }
    
    func reviewCheckIn(checkInId: String, approved: Bool, comment: String?, completion: @escaping (Result<Void, Error>) -> Void) {
        apiService.reviewCheckIn(checkInId: checkInId, approved: approved, comment: comment, completion: completion)
    }
    
    // MARK: - Offline Sync
    
    func syncOfflineCheckIns(completion: @escaping (Bool, Int, Int) -> Void) {
        offlineSyncManager.forceSyncNow(completion: completion)
    }
    
    func getPendingSyncCount() -> Int {
        return offlineSyncManager.getPendingSyncCount()
    }
}
