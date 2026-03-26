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
                    
                case .failure(let error):
                    let errorMessage = self?.parseErrorMessage(error) ?? "打卡失败"
                    self?.checkInState = .error(errorMessage)
                }
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
