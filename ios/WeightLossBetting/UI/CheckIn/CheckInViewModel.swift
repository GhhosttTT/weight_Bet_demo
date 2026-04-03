import Foundation

enum CheckInState {
    case idle
    case loading
    case success(CheckIn)
    case error(String)
}

enum PhotoUploadState {
    case idle
    case loading
    case success(String)
    case error(String)
}

class CheckInViewModel {
    private let checkInRepository = CheckInRepository.shared
    private let bettingPlanRepository = BettingPlanRepository.shared
    private let recommendationRepository = RecommendationRepository.shared
    
    var onCheckInStateChanged: ((CheckInState) -> Void)?
    var onPhotoUploadStateChanged: ((PhotoUploadState) -> Void)?
    
    private(set) var checkInState: CheckInState = .idle {
        didSet {
            onCheckInStateChanged?(checkInState)
        }
    }
    
    private(set) var photoUploadState: PhotoUploadState = .idle {
        didSet {
            onPhotoUploadStateChanged?(photoUploadState)
        }
    }
    
    private var uploadedPhotoUrl: String?
    private var currentPlanId: String?  // 当前进行中的计划 ID
    
    // MARK: - Photo Upload
    
    func uploadPhoto(imageData: Data, checkInId: String = UUID().uuidString) {
        photoUploadState = .loading
        
        checkInRepository.uploadCheckInPhoto(checkInId: checkInId, imageData: imageData) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let photoUrl):
                    self?.uploadedPhotoUrl = photoUrl
                    self?.photoUploadState = .success(photoUrl)
                    
                case .failure(let error):
                    self?.photoUploadState = .error(error.localizedDescription)
                }
            }
        }
    }
    
    // MARK: - Check-In
    
    /// 加载最近的一个进行中的计划
    func loadActivePlan(userId: String, completion: @escaping (Bool) -> Void) {
        bettingPlanRepository.getUserBettingPlans(userId: userId, forceRefresh: true) { [weak self] (result: Result<[BettingPlan], Error>) in
            switch result {
            case .success(let plans):
                // 过滤出进行中的计划，按创建时间排序，取最近的一个
                let activePlans = plans.filter { $0.status == .active }
                    .sorted { $0.createdAt > $1.createdAt }
                
                if let latestPlan = activePlans.first {
                    self?.currentPlanId = latestPlan.id
                    print("✅ Loaded latest active plan: \(latestPlan.id)")
                    completion(true)
                } else {
                    self?.currentPlanId = nil
                    print("⚠️ No active plans found")
                    completion(false)
                }
                
            case .failure(let error):
                print("❌ Failed to load active plans: \(error)")
                self?.currentPlanId = nil
                completion(false)
            }
        }
    }
    
    /// 自动打卡到最近的一个进行中的计划
    func createAutoCheckIn(weight: Double, note: String?) {
        guard let planId = currentPlanId else {
            checkInState = .error("暂无进行中的计划，请先创建或加入计划")
            return
        }
        
        createCheckIn(planId: planId, weight: weight, note: note)
    }
    
    func createCheckIn(planId: String, weight: Double, note: String?) {
        // Validate weight
        guard weight >= 30 && weight <= 300 else {
            checkInState = .error("体重必须在30-300kg之间")
            return
        }
        
        checkInState = .loading
        
        checkInRepository.createCheckIn(
            planId: planId,
            weight: weight,
            note: note,
            photoUrl: uploadedPhotoUrl
        ) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let checkIn):
                    self?.checkInState = .success(checkIn)
                    // Check-in successful, refresh recommendation in background
                    self?.refreshRecommendation()
                    
                case .failure(let error):
                    let errorMessage = self?.parseErrorMessage(error) ?? "打卡失败"
                    self?.checkInState = .error(errorMessage)
                }
            }
        }
    }
    
    /// Refresh recommendation after check-in
    private func refreshRecommendation() {
        print("🔵 [CheckInVM] Refreshing recommendation after check-in...")
        recommendationRepository.refreshRecommendation { result in
            switch result {
            case .success:
                print("✅ [CheckInVM] Recommendation refreshed successfully")
            case .failure(let error):
                print("⚠️ [CheckInVM] Failed to refresh recommendation: \(error.localizedDescription)")
            }
        }
    }
    
    private func parseErrorMessage(_ error: Error) -> String {
        let errorString = error.localizedDescription
        
        if errorString.contains("already checked in") || errorString.contains("重复打卡") {
            return "今日已打卡,请明天再来"
        } else if errorString.contains("out of range") || errorString.contains("日期") {
            return "打卡日期不在计划期间内"
        } else if errorString.contains("balance") || errorString.contains("余额") {
            return "账户余额不足"
        } else {
            return "打卡失败: \(errorString)"
        }
    }
}
