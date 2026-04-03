import Foundation
import UIKit

final class PendingActionsService {
    static let shared = PendingActionsService()
    private init() {}

    private lazy var repository = PendingActionsRepository()
    private let maxRetryCount = 3
    private let userDefaultsKey = "seen_pending_invitations"

    // MARK: - Public
    func checkAndHandlePendingActions() {
        Task {
            await self.fetchAndHandle()
        }
    }

    // MARK: - Internal flow
    private func fetchAndHandle() async {
        let result = await repository.fetchPendingActions()
        switch result {
        case .success(let data):
            await handlePendingActions(data)
        case .failure(let error):
            print("⚠️ Failed to fetch pending actions: \(error)")
        case .loading:
            break
        }
    }

    private func handlePendingActions(_ response: PendingActionsResponse) async {
        // Handle invitations first - 与安卓端对齐，不检查 isFirstTime
        if let invitations = response.invitations, invitations.count > 0 {
            for invite in invitations {
                // 只检查本地是否已显示过
                if await hasLocallySeen(invitationId: invite.id) {
                    continue
                }

                await presentInviteModal(invite)
            }
        }

        // Handle double checks
        if let doubleChecks = response.doubleChecks, doubleChecks.count > 0 {
            // 获取当前登录用户ID
            guard let currentUserId = AuthRepository.shared.getCurrentUserId() else { return }
            
            for dc in doubleChecks where (dc.isPending ?? false) {
                // 二次确认仅推送给计划创建者，initiatorId是接受计划的参与者，所以当前用户不是initiatorId才弹窗
                guard dc.initiatorId != currentUserId else { continue }
                
                // 检查本地是否已显示过
                let seenId = "double_check_\(dc.planId)"
                if await hasLocallySeen(invitationId: seenId) {
                    continue
                }
                
                await presentDoubleCheckModal(dc)
            }
        }
        
        // Handle settlements - 与安卓端对齐
        if let settlements = response.settlements, settlements.count > 0 {
            for settlement in settlements {
                await presentSettlementModal(settlement)
            }
        }
    }

    // MARK: - Modals
    private func presentInviteModal(_ invite: InvitationItem) async {
        await MainActor.run {
            guard let top = topViewController() else { return }
            let vc = OneTimeInviteModalViewController(invitation: invite)
            vc.onDisplayed = { [weak self] in
                // Mark locally to avoid re-show until mark-seen confirmed
                Task {
                    await self?.markLocallySeen(invitationId: invite.id)
                }
            }
            vc.onDismiss = { [weak self] success in
                guard let self = self else { return }
                if success {
                    Task {
                        await self.markInvitationSeenWithRetry(invitationId: invite.id)
                    }
                } else {
                    // Allow future fetch to show again; remove local mark
                    Task {
                        await self.clearLocalSeen(invitationId: invite.id)
                    }
                }
            }

            top.present(vc, animated: true, completion: nil)
        }
    }

    private func presentDoubleCheckModal(_ dc: DoubleCheckItem) async {
        let seenId = "double_check_\(dc.planId)"
        
        await MainActor.run {
            guard let top = topViewController() else { return }
            let vc = DoubleCheckModalViewController(item: dc)
            
            // 弹窗显示后立即标记为已查看，防止重复弹出
            vc.onDisplayed = {
                Task {
                    await self.markLocallySeen(invitationId: seenId)
                }
            }
            
            vc.onDismiss = { [weak self] viewed in
                guard let self = self else { return }
                Task {
                    if viewed {
                        // 用户点击了查看，永久标记为已处理
                        await self.persistFinalSeen(invitationId: seenId)
                    } else {
                        // 用户点击了稍后再看，保留本地标记，不再弹出
                        // 符合需求：点击稍后再看下次进入APP不重复弹出
                    }
                }
            }

            top.present(vc, animated: true, completion: nil)
        }
    }
    
    private func presentSettlementModal(_ settlement: SettlementItem) async {
        await MainActor.run {
            guard let top = topViewController() else { return }
            // TODO: 实现结算弹窗
            print("📋 [PendingActions] 显示结算弹窗：\(settlement.planId)")
        }
    }

    // MARK: - Network with retry
    private func markInvitationSeenWithRetry(invitationId: String, attempt: Int = 1) async {
        let result = await repository.markInvitationSeen(invitationId: invitationId, userId: nil)
        switch result {
        case .success:
            print("✅ Marked invitation \(invitationId) as seen")
            // persist final seen
            await persistFinalSeen(invitationId: invitationId)
        case .failure(let error):
            print("❌ Failed to mark invitation seen (attempt \(attempt)): \(error)")
            if attempt < maxRetryCount {
                // simple linear retry with delay
                try? await Task.sleep(nanoseconds: UInt64(1_000_000_000))
                await markInvitationSeenWithRetry(invitationId: invitationId, attempt: attempt + 1)
            } else {
                // give up for now, clear local mark so it can be shown later
                await clearLocalSeen(invitationId: invitationId)
                // enqueue to persistent retry queue for background processing
                let action = PendingNetworkAction(id: invitationId,
                                                  type: .markSeen,
                                                  parameters: ["userId": ""],
                                                  attempt: attempt,
                                                  createdAt: Date())
                await PendingActionsRetryQueue.shared.add(action: action)
                // trigger background processing
                Task {
                    await PendingActionsRetryQueue.shared.processQueue()
                }
            }
        case .loading:
            break
        }
    }

    private func postDoubleCheckWithRetry(planId: String, action: String, comment: String?, attempt: Int = 1) async {
        var parameters: [String: Any] = ["action": action]
        if let comment = comment { parameters["comment"] = comment }

        let result = await repository.postDoubleCheck(planId: planId, parameters: parameters)
        switch result {
        case .success:
            print("✅ Double-check posted successfully for plan \(planId)")
            // trigger background processing
            Task {
                await PendingActionsRetryQueue.shared.processQueue()
            }
        case .failure(let error):
            print("❌ Failed double-check (attempt \(attempt)): \(error)")
            if attempt < maxRetryCount {
                try? await Task.sleep(nanoseconds: UInt64(1_000_000_000))
                await postDoubleCheckWithRetry(planId: planId, action: action, comment: comment, attempt: attempt + 1)
            } else {
                // final failure - enqueue persistent retry
                var params: [String: String] = ["action": action]
                if let c = comment { params["comment"] = c }
                let netAction = PendingNetworkAction(id: planId,
                                                     type: .doubleCheck,
                                                     parameters: params,
                                                     attempt: attempt,
                                                     createdAt: Date())
                await PendingActionsRetryQueue.shared.add(action: netAction)
                Task {
                    await PendingActionsRetryQueue.shared.processQueue()
                }
            }
        case .loading:
            break
        }
    }

    // MARK: - Local seen tracking (simple)
    private func hasLocallySeen(invitationId: String) async -> Bool {
        return await PendingActionsCoreStore.shared.hasSeenInvitation(id: invitationId)
    }

    private func markLocallySeen(invitationId: String) async {
        await PendingActionsCoreStore.shared.addSeenInvitation(id: invitationId)
    }

    private func clearLocalSeen(invitationId: String) async {
        await PendingActionsCoreStore.shared.removeSeenInvitation(id: invitationId)
    }

    private func persistFinalSeen(invitationId: String) async {
        // For now same as local; could be extended to store in a different key
        await markLocallySeen(invitationId: invitationId)
    }

    // MARK: - Helpers
    private func topViewController() -> UIViewController? {
        guard let window = UIApplication.shared.connectedScenes
                .compactMap({ $0 as? UIWindowScene })
                .first?.windows.first(where: { $0.isKeyWindow }) else { return nil }

        var top = window.rootViewController
        while let presented = top?.presentedViewController {
            top = presented
        }
        return top
    }
}
