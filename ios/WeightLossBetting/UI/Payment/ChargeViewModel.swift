import Foundation

enum ChargeState {
    case idle
    case loading
    case awaitingConfirmation(String)
    case success
    case error(String)
}

final class ChargeViewModel {
    private let paymentRepository = PaymentRepository()
    var onChargeStateChanged: ((ChargeState) -> Void)?
    private var chargeIdempotencyKey: String?
    private var chargeState: ChargeState = .idle {
        didSet { onChargeStateChanged?(chargeState) }
    }

    func charge(amount: Double) {
        chargeState = .loading
        Task {
            let idempotencyKey = chargeIdempotencyKey ?? UUID().uuidString
            chargeIdempotencyKey = idempotencyKey
            let result = await paymentRepository.createChargeIntent(
                amount: amount,
                idempotencyKey: idempotencyKey
            )
            switch result {
            case .success(let intent):
                guard let clientSecret = intent.clientSecret, !clientSecret.isEmpty else {
                    chargeState = .error("支付订单缺少确认凭证")
                    return
                }
                chargeState = .awaitingConfirmation(clientSecret)
            case .failure(let error):
                chargeState = .error(parseError(error))
            case .loading:
                break
            }
        }
    }

    func paymentCompleted() { chargeIdempotencyKey = nil; chargeState = .success }
    func paymentCanceled() { chargeIdempotencyKey = nil; chargeState = .error("已取消支付") }
    func paymentFailed(_ message: String) {
        // Stripe 已明确拒绝当前 PaymentIntent；下一次重试必须创建新的
        // 本地交易和 Stripe 幂等键，避免重复复用已失败的 PaymentIntent。
        chargeIdempotencyKey = nil
        chargeState = .error(message)
    }

    private func parseError(_ error: Error) -> String {
        if let networkError = error as? NetworkError {
            switch networkError {
            case .networkError(let message): return "网络错误: \(message)"
            case .unauthorizedError: return "未授权，请重新登录"
            case .validationError(let message): return "验证错误: \(message)"
            case .serverError(_, let message): return "服务器错误: \(message)"
            case .timeoutError(let message): return "请求超时: \(message)"
            case .unknownError(let message): return message
            }
        }
        return error.localizedDescription
    }
}
