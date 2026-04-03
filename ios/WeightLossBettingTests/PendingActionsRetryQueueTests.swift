import XCTest
@testable import WeightLossBetting

final class PendingActionsRetryQueueTests: XCTestCase {

    override func setUp() {
        super.setUp()
        // Clear stored queue
        UserDefaults.standard.removeObject(forKey: "pending_network_actions_queue")
    }

    override func tearDown() {
        UserDefaults.standard.removeObject(forKey: "pending_network_actions_queue")
        super.tearDown()
    }

    func testAddAndPersistAction() async throws {
        let action = PendingNetworkAction(id: "inv123", type: .markSeen, parameters: ["userId": "user_b"], attempt: 0, createdAt: Date())
        await PendingActionsRetryQueue.shared.add(action: action)
        
        // Give it a moment to persist
        try await Task.sleep(nanoseconds: 100_000_000)

        // Read raw data from UserDefaults and decode
        guard let data = UserDefaults.standard.data(forKey: "pending_network_actions_queue") else {
            XCTFail("No data persisted")
            return
        }

        let decoder = JSONDecoder()
        do {
            let arr = try decoder.decode([PendingNetworkAction].self, from: data)
            XCTAssertEqual(arr.count, 1)
            XCTAssertEqual(arr.first?.id, "inv123")
            XCTAssertEqual(arr.first?.type, .markSeen)
            XCTAssertEqual(arr.first?.parameters?["userId"], "user_b")
        } catch {
            XCTFail("Decoding failed: \(error)")
        }
    }
}

