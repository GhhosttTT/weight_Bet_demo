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
    private var pendingPhotoData: Data?
    private var currentPlanId: String?  // 当前进行中的计划 ID
    
    // MARK: - Photo Upload
    
    func uploadPhoto(
        imageData: Data,
        checkInId: String? = nil,
        completion: ((Result<String, Error>) -> Void)? = nil
    ) {
        // 选图时先暂存，创建打卡后使用服务端返回的真实 ID 上传。
        guard let checkInId = checkInId else {
            pendingPhotoData = imageData
            photoUploadState = .success("pending")
            return
        }

        photoUploadState = .loading
        
        checkInRepository.uploadCheckInPhoto(checkInId: checkInId, imageData: imageData) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let photoUrl):
                    self?.uploadedPhotoUrl = photoUrl
                    self?.photoUploadState = .success(photoUrl)
                    completion?(.success(photoUrl))
                    
                case .failure(let error):
                    self?.photoUploadState = .error(error.localizedDescription)
                    completion?(.failure(error))
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
            photoUrl: nil
        ) { [weak self] result in
            DispatchQueue.main.async {
                switch result {
                case .success(let checkIn):
                    guard let self = self, let imageData = self.pendingPhotoData else {
                        self?.checkInState = .success(checkIn)
                        self?.refreshRecommendation()
                        return
                    }

                    // 图片上传完成后再向页面报告最终成功状态。
                    self.uploadPhoto(imageData: imageData, checkInId: checkIn.id) { [weak self] uploadResult in
                        guard let self = self else { return }
                        switch uploadResult {
                        case .success:
                            self.pendingPhotoData = nil
                            self.checkInState = .success(checkIn)
                            self.refreshRecommendation()
                        case .failure(let error):
                            self.checkInState = .error("打卡已成功，但照片上传失败：\(error.localizedDescription)")
                        }
                    }
                    
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
