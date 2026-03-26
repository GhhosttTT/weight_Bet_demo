import Foundation

class ProgressViewModel {
    private let checkInRepository = CheckInRepository.shared
    
    var onProgressUpdated: ((ProgressStats) -> Void)?
    var onLoadingChanged: ((Bool) -> Void)?
    var onError: ((String) -> Void)?
    
    func loadProgress(planId: String, userId: String) {
        onLoadingChanged?(true)
        
        checkInRepository.getProgress(planId: planId, userId: userId) { [weak self] result in
            DispatchQueue.main.async {
                self?.onLoadingChanged?(false)
                
                switch result {
                case .success(let stats):
                    self?.onProgressUpdated?(stats)
                    
                case .failure(let error):
                    self?.onError?(error.localizedDescription)
                }
            }
        }
    }
}
