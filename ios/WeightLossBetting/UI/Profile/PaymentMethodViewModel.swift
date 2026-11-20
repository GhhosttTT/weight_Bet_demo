import Foundation

enum PaymentMethodState {
    case idle
    case loading
    case setupIntentReady(String)
    case success
    case error(String)
}

final class PaymentMethodViewModel {
    private let paymentRepository = PaymentRepository.shared
    var onStateChanged: ((PaymentMethodState) -> Void)?

    private var state: PaymentMethodState = .idle {
        didSet { onStateChanged?(state) }
    }

    func createSetupIntent() {
        state = .loading
        Task {
            let result = await paymentRepository.createSetupIntent()
            switch result {
            case .success(let intent):
                guard let clientSecret = intent.clientSecret, !clientSecret.isEmpty else {
                    state = .error("支付方式初始化缺少确认凭证")
                    return
                }
                state = .setupIntentReady(clientSecret)
            case .failure(let error):
                state = .error(error.localizedDescription)
            case .loading:
                break
            }
        }
    }

    func setupCompleted() { state = .success }
    func setupCanceled() { state = .idle }
    func setupFailed(_ message: String) { state = .error(message) }
}
