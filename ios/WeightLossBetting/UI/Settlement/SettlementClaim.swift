//
//  SettlementClaim.swift
//  WeightLossBetting
//
//  Created by AI Assistant on 2026-03-25.
//

import Foundation

struct SettlementClaim {
    let planId: String
    let userId: String
    let myAchievement: Bool
    let opponentAchievement: Bool
    let timestamp: Date

    init(planId: String, userId: String, myAchievement: Bool, opponentAchievement: Bool) {
        self.planId = planId
        self.userId = userId
        self.myAchievement = myAchievement
        self.opponentAchievement = opponentAchievement
        self.timestamp = Date()
    }
}

struct SettlementResult {
    let planId: String
    let creatorAchieved: Bool
    let participantAchieved: Bool
    let creatorAmount: Double
    let participantAmount: Double
    let platformFee: Double
    let settlementDate: Date
    let inArbitration: Bool?
}
