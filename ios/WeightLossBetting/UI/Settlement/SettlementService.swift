//
//  SettlementService.swift
//  WeightLossBetting
//
//  Created by AI Assistant on 2026-03-25.
//

import Foundation

class SettlementService {

    static let shared = SettlementService()
    private init() {}

    // Submit settlement claim
    func submitSettlementClaim(planId: String, myAchievement: Bool, opponentAchievement: Bool, completion: @escaping (Result<Void, Error>) -> Void) {
        APIService.shared.submitSettlementChoice(
            planId: planId,
            selfAchieved: myAchievement,
            opponentAchieved: opponentAchievement
        ) { result in
            switch result {
            case .success:
                completion(.success(()))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }

    func getSettlementSelectionStatus(
        planId: String,
        completion: @escaping (Result<SettlementSelectionStatus, Error>) -> Void
    ) {
        APIService.shared.getSettlementSelectionStatus(planId: planId, completion: completion)
    }

}
