import Foundation

class CheckInHistoryViewModel {
    private let checkInRepository = CheckInRepository.shared
    
    var onCheckInsUpdated: (() -> Void)?
    var onLoadingChanged: ((Bool) -> Void)?
    var onError: ((String) -> Void)?
    
    private(set) var checkIns: [CheckIn] = [] {
        didSet {
            onCheckInsUpdated?()
        }
    }
    
    func loadCheckIns(planId: String, userId: String?, forceRefresh: Bool = false) {
        onLoadingChanged?(true)
        
        checkInRepository.getCheckInHistory(planId: planId, userId: userId, forceRefresh: forceRefresh) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let checkIns):
                    self?.checkIns = checkIns.sorted { $0.checkInDate > $1.checkInDate }
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
}
