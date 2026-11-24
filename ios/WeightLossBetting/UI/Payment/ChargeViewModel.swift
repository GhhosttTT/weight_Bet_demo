import Foundation

enum ChargeState {
    case idle
    case loading
    case awaitingConfirmation(String, String)
    case awaitingWebhook
    case success
    case error(String)
}

final class ChargeViewModel {
    private let paymentRepository = PaymentRepository()
    var onChargeStateChanged: ((ChargeState) -> Void)?
    private var chargeIdempotencyKey: String?
    private var pendingTransactionId: String? = {
        if let secureValue = TokenManager.shared.getPendingCharge() {
            return secureValue
        }
        // 兼容旧版本的未完成充值订单，并立即迁移到 Keychain。
        guard let legacyValue = UserDefaults.standard.string(forKey: "pendingChargeTransactionId") else {
            return nil
        }
        TokenManager.shared.savePendingCharge(legacyValue)
        UserDefaults.standard.removeObject(forKey: "pendingChargeTransactionId")
        return legacyValue
    }()
    private var chargeState: ChargeState = .idle {
        didSet { onChargeStateChanged?(chargeState) }
    }

    func charge(amount: Double) {
        guard amount.isFinite, amount > 0 else {
            chargeState = .error("充值金额必须大于0")
            return
        }
        guard amount >= 0.01 else {
            chargeState = .error("充值金额不能少于0.01元")
            return
        }
        guard amount <= 10000 else {
            chargeState = .error("单次充值金额不能超过10000元")
            return
        }
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
                pendingTransactionId = intent.transactionId
                TokenManager.shared.savePendingCharge(intent.transactionId)
                chargeState = .awaitingConfirmation(clientSecret, intent.transactionId)
            case .failure(let error):
                chargeState = .error(parseError(error))
            case .loading:
                break
            }
        }
    }

    func paymentCompleted() {
        guard let transactionId = pendingTransactionId else {
            chargeState = .error("支付订单状态已变化，请刷新后重试")
            return
        }
        chargeState = .awaitingWebhook
        Task {
            for attempt in 0..<12 {
                let result = await paymentRepository.getTransactionStatus(transactionId: transactionId)
                switch result {
                case .success(let status):
                    if status.status.lowercased() == "completed" {
                        chargeIdempotencyKey = nil
                        pendingTransactionId = nil
                        TokenManager.shared.clearPendingCharge()
                        chargeState = .success
                        return
                    }
                    if status.status.lowercased() == "failed" {
                        chargeIdempotencyKey = nil
                        pendingTransactionId = nil
                        TokenManager.shared.clearPendingCharge()
                        chargeState = .error("支付已失败，请重新尝试")
                        return
                    }
                case .failure:
                    if attempt == 11 {
                        chargeState = .error("支付已确认，入账处理中，请稍后刷新余额")
                        return
                    }
                case .loading:
                    break
                }
                try? await Task.sleep(nanoseconds: 1_000_000_000)
            }
            chargeState = .error("支付已确认，入账处理中，请稍后刷新余额")
        }
    }
    func paymentCanceled() {
        // 保留服务端 pending 交易以便恢复，但下一次改金额必须使用新幂等键。
        chargeIdempotencyKey = nil
        chargeState = .error("已取消支付")
    }
    func paymentFailed(_ message: String) {
        // Stripe 已明确拒绝当前 PaymentIntent；下一次重试必须创建新的
        // 本地交易和 Stripe 幂等键，避免重复复用已失败的 PaymentIntent。
        chargeIdempotencyKey = nil
        pendingTransactionId = nil
        TokenManager.shared.clearPendingCharge()
        chargeState = .error(message)
    }

    func restorePendingCharge() {
        guard let transactionId = pendingTransactionId else { return }
        Task {
            switch await paymentRepository.resumeChargeIntent(transactionId: transactionId) {
            case .success(let intent):
                if ["canceled", "failed"].contains(intent.status.lowercased()) {
                    paymentFailed("未完成充值订单已取消，请重新发起充值")
                    return
                }
                guard let secret = intent.clientSecret, !secret.isEmpty else {
                    chargeState = .error("未完成订单缺少支付凭证")
                    return
                }
                if intent.status.lowercased() == "succeeded" {
                    paymentCompleted()
                } else {
                    chargeState = .awaitingConfirmation(secret, transactionId)
                }
            case .failure:
                chargeState = .error("未完成充值订单恢复失败，请刷新交易记录")
            case .loading:
                break
            }
        }
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
