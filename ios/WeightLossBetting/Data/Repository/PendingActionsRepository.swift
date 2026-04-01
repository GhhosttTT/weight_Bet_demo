import Foundation

protocol PendingActionsRepositoryProtocol {
    func fetchPendingActions() async -> NetworkResult<PendingActionsResponse>
    func markInvitationSeen(invitationId: String, userId: String?) async -> NetworkResult<Void>
    func postDoubleCheck(planId: String, parameters: [String: Any]) async -> NetworkResult<Void>
}

class PendingActionsRepository: BaseRepository, PendingActionsRepositoryProtocol {
    private lazy var api = APIService.shared

    func fetchPendingActions() async -> NetworkResult<PendingActionsResponse> {
        return await safeApiCall { [self] completion in
            api.getPendingActions { result in
                completion(result)
            }
        }
    }

    func markInvitationSeen(invitationId: String, userId: String?) async -> NetworkResult<Void> {
        return await safeApiCall { [self] completion in
            api.markInvitationSeen(invitationId: invitationId, userId: userId) { result in
                completion(result)
            }
        }
    }

    func postDoubleCheck(planId: String, parameters: [String: Any]) async -> NetworkResult<Void> {
        return await safeApiCall { [self] completion in
            api.postDoubleCheck(planId: planId, parameters: parameters) { result in
                completion(result)
            }
        }
    }
}
