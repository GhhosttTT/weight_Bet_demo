import Foundation

enum PendingActionType: String, Codable {
    case markSeen
    case doubleCheck
}

struct PendingNetworkAction: Codable {
    let id: String // invitation id or plan id
    let type: PendingActionType
    var parameters: [String: String]? // simple string map for persistence
    var attempt: Int
    var createdAt: Date
}

final class PendingActionsRetryQueue {
    static let shared = PendingActionsRetryQueue()
    // Allow creating instances with injected repository for tests
    init(repository: PendingActionsRepositoryProtocol = PendingActionsRepository()) {
        self.repository = repository
        // Migrate old UserDefaults data into CoreData-backed store
        // 我们需要异步调用迁移方法，所以使用 Task 来包装
        Task { 
            await PendingActionsCoreStore.shared.migrateFromUserDefaults(oldQueueKey: "pending_network_actions_queue", oldSeenKey: "seen_pending_invitations")
        }
    }

    // 可注入仓库用于测试
    private let repository: PendingActionsRepositoryProtocol

    private let coreStore = PendingActionsCoreStore.shared
    private let maxAttempts = 5

    private func fetchQueue() async -> [PendingNetworkAction] {
        return await coreStore.fetchPendingNetworkActions()
    }

    func add(action: PendingNetworkAction) async {
        await coreStore.addPendingNetworkAction(action)
    }

    func remove(id: String, type: PendingActionType) async {
        await coreStore.removePendingNetworkAction(id: id, type: type)
    }

    func processQueue() async {
        var arr = await coreStore.fetchPendingNetworkActions()
        guard arr.count > 0 else { return }

        for (index, var action) in arr.enumerated().reversed() {
            if action.attempt >= maxAttempts {
                // drop it
                await coreStore.removePendingNetworkAction(id: action.id, type: action.type)
                continue
            }

            // exponential backoff delay based on attempt
            let delaySeconds = pow(2.0, Double(action.attempt))
            if action.attempt > 0 {
                try? await Task.sleep(nanoseconds: UInt64(delaySeconds * 1_000_000_000))
            }

            switch action.type {
            case .markSeen:
                let result = await repository.markInvitationSeen(invitationId: action.id, userId: action.parameters?["userId"])
                switch result {
                case .success:
                    print("✅ Retry queue: marked invitation \(action.id) seen")
                    await coreStore.removePendingNetworkAction(id: action.id, type: action.type)
                case .failure(let error):
                    print("⚠️ Retry queue: failed to mark seen \(action.id): \(error). attempt \(action.attempt + 1)")
                    action.attempt += 1
                    await coreStore.updateAttempt(for: action.id, type: action.type, attempt: action.attempt)
                case .loading:
                    // Do nothing, continue to next iteration
                    break
                }

            case .doubleCheck:
                var params: [String: Any] = [:]
                if let p = action.parameters {
                    if let actionStr = p["action"] { params["action"] = actionStr }
                    if let comment = p["comment"] { params["comment"] = comment }
                    if let userId = p["userId"] { params["userId"] = userId }
                }
                let result = await repository.postDoubleCheck(planId: action.id, parameters: params)
                switch result {
                case .success:
                    print("✅ Retry queue: posted doublecheck for plan \(action.id)")
                    await coreStore.removePendingNetworkAction(id: action.id, type: action.type)
                case .failure(let error):
                    print("⚠️ Retry queue: failed doublecheck \(action.id): \(error). attempt \(action.attempt + 1)")
                    action.attempt += 1
                    await coreStore.updateAttempt(for: action.id, type: action.type, attempt: action.attempt)
                case .loading:
                    // Do nothing, continue to next iteration
                    break
                }
            }
        }
    }
}
