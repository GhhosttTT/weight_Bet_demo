//
//  SettlementService.swift
//  WeightLossBetting
//
//  Created by AI Assistant on 2026-03-25.
//

import Foundation

class SettlementService {

    static let shared = SettlementService()
    private let baseURL = "https://api.weightlossbetting.com" // Replace with actual API URL

    private init() {}

    // Submit settlement claim
    func submitSettlementClaim(planId: String, myAchievement: Bool, opponentAchievement: Bool, completion: @escaping (Result<Void, Error>) -> Void) {
        guard let userId = UserManager.shared.currentUser?.id else {
            completion(.failure(NSError(domain: "SettlementService", code: -1, userInfo: [NSLocalizedDescriptionKey: "User not logged in"])))
            return
        }

        let url = URL(string: "\(baseURL)/settlements/claim")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // Add auth token
        if let token = AuthManager.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let body: [String: Any] = [
            "planId": planId,
            "userId": userId,
            "myAchievement": myAchievement,
            "opponentAchievement": opponentAchievement
        ]

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            completion(.failure(error))
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                completion(.failure(NSError(domain: "SettlementService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                return
            }

            completion(.success(()))
        }.resume()
    }

    // Get settlement status for a plan
    func getSettlementStatus(planId: String, completion: @escaping (Result<SettlementResult?, Error>) -> Void) {
        let url = URL(string: "\(baseURL)/settlements/plan/\(planId)")!
        var request = URLRequest(url: url)
        request.httpMethod = "GET"

        // Add auth token
        if let token = AuthManager.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let httpResponse = response as? HTTPURLResponse else {
                completion(.failure(NSError(domain: "SettlementService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                return
            }

            if httpResponse.statusCode == 404 {
                // No settlement yet
                completion(.success(nil))
                return
            }

            guard (200...299).contains(httpResponse.statusCode),
                  let data = data else {
                completion(.failure(NSError(domain: "SettlementService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                return
            }

            do {
                let json = try JSONSerialization.jsonObject(with: data) as? [String: Any]
                // Parse settlement result
                let dateFormatter = ISO8601DateFormatter()
                let settlementDate = json?["settlement_date"] as? String ?? ""
                let parsedDate = dateFormatter.date(from: settlementDate) ?? Date()
                let settlement = SettlementResult(
                    planId: planId,
                    creatorAchieved: json?["creator_achieved"] as? Bool ?? false,
                    participantAchieved: json?["participant_achieved"] as? Bool ?? false,
                    creatorAmount: json?["creator_amount"] as? Double ?? 0,
                    participantAmount: json?["participant_amount"] as? Double ?? 0,
                    platformFee: json?["platform_fee"] as? Double ?? 0,
                    settlementDate: parsedDate,
                    inArbitration: json?["in_arbitration"] as? Bool
                )
                completion(.success(settlement))
            } catch {
                completion(.failure(error))
            }
        }.resume()
    }

    // Submit arbitration evidence
    func submitArbitrationEvidence(planId: String, videoURL: URL, weight: Double, completion: @escaping (Result<Void, Error>) -> Void) {
        guard let userId = UserManager.shared.currentUser?.id else {
            completion(.failure(NSError(domain: "SettlementService", code: -1, userInfo: [NSLocalizedDescriptionKey: "User not logged in"])))
            return
        }

        let url = URL(string: "\(baseURL)/settlements/arbitration")!
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // Add auth token
        if let token = AuthManager.shared.accessToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        let body: [String: Any] = [
            "planId": planId,
            "userId": userId,
            "videoURL": videoURL.absoluteString,
            "weight": weight
        ]

        do {
            request.httpBody = try JSONSerialization.data(withJSONObject: body)
        } catch {
            completion(.failure(error))
            return
        }

        URLSession.shared.dataTask(with: request) { data, response, error in
            if let error = error {
                completion(.failure(error))
                return
            }

            guard let httpResponse = response as? HTTPURLResponse,
                  (200...299).contains(httpResponse.statusCode) else {
                completion(.failure(NSError(domain: "SettlementService", code: -1, userInfo: [NSLocalizedDescriptionKey: "Invalid response"])))
                return
            }

            completion(.success(()))
        }.resume()
    }
}
