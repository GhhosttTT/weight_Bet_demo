import Foundation
import Network

class OfflineSyncManager {
    static let shared = OfflineSyncManager()
    
    private let coreDataManager = CoreDataManager.shared
    private let apiService = APIService.shared
    private let monitor = NWPathMonitor()
    private let queue = DispatchQueue(label: "com.weightlossbetting.offlineSync")
    
    private var isOnline = false
    private var isSyncing = false
    
    private init() {
        setupNetworkMonitoring()
    }
    
    // MARK: - Network Monitoring
    
    private func setupNetworkMonitoring() {
        monitor.pathUpdateHandler = { [weak self] path in
            let wasOffline = !(self?.isOnline ?? false)
            self?.isOnline = path.status == .satisfied
            
            // If we just came online, sync offline data
            if wasOffline && (self?.isOnline ?? false) {
                self?.syncOfflineData()
            }
        }
        
        monitor.start(queue: queue)
    }
    
    // MARK: - Offline Check-In Management
    
    func saveOfflineCheckIn(planId: String, weight: Double, note: String?, photoUrl: String?) {
        coreDataManager.saveOfflineCheckIn(
            planId: planId,
            weight: weight,
            note: note,
            photoUrl: photoUrl
        )
        
        // Try to sync immediately if online
        if isOnline {
            syncOfflineData()
        }
    }
    
    // MARK: - Sync Management
    
    func syncOfflineData() {
        guard isOnline && !isSyncing else { return }
        
        isSyncing = true
        
        let offlineCheckIns = coreDataManager.getOfflineCheckIns()
        
        guard !offlineCheckIns.isEmpty else {
            isSyncing = false
            return
        }
        
        print("Syncing \(offlineCheckIns.count) offline check-ins...")
        
        let group = DispatchGroup()
        var syncedCount = 0
        var failedCount = 0
        
        for checkIn in offlineCheckIns {
            group.enter()
            
            syncCheckIn(checkIn) { success in
                if success {
                    syncedCount += 1
                } else {
                    failedCount += 1
                }
                group.leave()
            }
        }
        
        group.notify(queue: .main) { [weak self] in
            self?.isSyncing = false
            print("Sync completed: \(syncedCount) succeeded, \(failedCount) failed")
            
            // Post notification for UI update
            NotificationCenter.default.post(
                name: NSNotification.Name("OfflineSyncCompleted"),
                object: nil,
                userInfo: ["synced": syncedCount, "failed": failedCount]
            )
        }
    }
    
    private func syncCheckIn(_ checkIn: OfflineCheckInEntity, completion: @escaping (Bool) -> Void) {
        guard let planId = checkIn.planId else {
            completion(false)
            return
        }
        
        // Get current user ID (should be stored in UserDefaults or Keychain)
        guard let userId = UserDefaults.standard.string(forKey: "currentUserId") else {
            completion(false)
            return
        }
        
        var parameters: [String: Any] = [
            "user_id": userId,
            "plan_id": planId,
            "weight": checkIn.weight,
            "check_in_date": ISO8601DateFormatter().string(from: checkIn.createdAt ?? Date())
        ]
        
        if let note = checkIn.note {
            parameters["note"] = note
        }
        
        if let photoUrl = checkIn.photoUrl {
            parameters["photo_url"] = photoUrl
        }
        
        apiService.createCheckIn(parameters: parameters) { [weak self] result in
            switch result {
            case .success:
                // Mark as synced
                if let id = checkIn.id {
                    self?.coreDataManager.markCheckInAsSynced(id: id)
                }
                completion(true)
                
            case .failure(let error):
                print("Failed to sync check-in: \(error.localizedDescription)")
                completion(false)
            }
        }
    }
    
    // MARK: - Manual Sync
    
    func forceSyncNow(completion: @escaping (Bool, Int, Int) -> Void) {
        guard isOnline else {
            completion(false, 0, 0)
            return
        }
        
        let offlineCheckIns = coreDataManager.getOfflineCheckIns()
        
        guard !offlineCheckIns.isEmpty else {
            completion(true, 0, 0)
            return
        }
        
        let group = DispatchGroup()
        var syncedCount = 0
        var failedCount = 0
        
        for checkIn in offlineCheckIns {
            group.enter()
            
            syncCheckIn(checkIn) { success in
                if success {
                    syncedCount += 1
                } else {
                    failedCount += 1
                }
                group.leave()
            }
        }
        
        group.notify(queue: .main) {
            completion(true, syncedCount, failedCount)
        }
    }
    
    // MARK: - Status
    
    func getPendingSyncCount() -> Int {
        return coreDataManager.getOfflineCheckIns().count
    }
    
    func isNetworkAvailable() -> Bool {
        return isOnline
    }
}
