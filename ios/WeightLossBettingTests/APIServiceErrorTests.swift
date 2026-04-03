import XCTest
@testable import WeightLossBetting

class APIServiceErrorTests: XCTestCase {
    
    var apiService: APIService!
    
    override func setUpWithError() throws {
        try super.setUpWithError()
        apiService = APIService.shared
    }
    
    override func tearDownWithError() throws {
        apiService = nil
        try super.tearDownWithError()
    }
    
    // MARK: - 认证接口错误测试
    
    func testLoginWithInvalidCredentials() async {
        let expectation = self.expectation(description: "Login should fail with invalid credentials")
        
        await apiService.login(email: "invalid@example.com", password: "wrongpassword") { result in
            switch result {
            case .success:
                XCTFail("Login should not succeed with invalid credentials")
            case .failure(let error):
                print("✅ Login error test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        await waitForExpectations(timeout: 10)
    }
    
    func testLoginWithInvalidEmailFormat() {
        let expectation = self.expectation(description: "Login should fail with invalid email format")
        
        apiService.login(email: "invalid-email", password: "password123") { result in
            switch result {
            case .success:
                XCTFail("Login should not succeed with invalid email format")
            case .failure(let error):
                print("✅ Invalid email format test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        waitForExpectations(timeout: 10)
    }
    
    func testRegisterWithWeakPassword() {
        let expectation = self.expectation(description: "Register should fail with weak password")
        
        apiService.register(email: "test@example.com", password: "123", nickname: "TestUser") { result in
            switch result {
            case .success:
                XCTFail("Register should not succeed with weak password")
            case .failure(let error):
                print("✅ Weak password test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        waitForExpectations(timeout: 10)
    }
    
    func testRegisterWithExistingEmail() {
        let expectation = self.expectation(description: "Register should fail with existing email")
        
        // Use the test account that should already exist
        apiService.register(email: "test1@qq.com", password: "newpassword123", nickname: "NewUser") { result in
            switch result {
            case .success:
                XCTFail("Register should not succeed with existing email")
            case .failure(let error):
                print("✅ Existing email test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        waitForExpectations(timeout: 10)
    }
    
    // MARK: - 用户接口错误测试
    
    func testGetUserProfileWithInvalidUserId() {
        let expectation = self.expectation(description: "Get user profile should fail with invalid ID")
        
        apiService.getUserProfile(userId: "invalid-user-id") { result in
            switch result {
            case .success:
                XCTFail("Get user profile should not succeed with invalid ID")
            case .failure(let error):
                print("✅ Invalid user ID test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        waitForExpectations(timeout: 10)
    }
    
    // MARK: - 对赌计划接口错误测试
    
    func testGetBettingPlanWithInvalidId() {
        let expectation = self.expectation(description: "Get betting plan should fail with invalid ID")
        
        apiService.getBettingPlan(planId: "invalid-plan-id") { result in
            switch result {
            case .success:
                XCTFail("Get betting plan should not succeed with invalid ID")
            case .failure(let error):
                print("✅ Invalid plan ID test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        waitForExpectations(timeout: 10)
    }
    
    // MARK: - 支付接口错误测试
    
    func testGetBalanceWithInvalidUserId() {
        let expectation = self.expectation(description: "Get balance should fail with invalid user ID")
        
        apiService.getBalance(userId: "invalid-user-id") { result in
            switch result {
            case .success:
                XCTFail("Get balance should not succeed with invalid user ID")
            case .failure(let error):
                print("✅ Invalid user ID for balance test passed: \(error.localizedDescription)")
                expectation.fulfill()
            }
        }
        
        waitForExpectations(timeout: 10)
    }
    
    // MARK: - 网络错误测试
    
    func testNetworkTimeout() {
        // This test verifies network timeout handling
        // Would need to mock the network layer for proper testing
        print("⚠️ Network timeout test requires mocking infrastructure")
    }
    
    func testServerUnavailable() {
        // Test when server is completely unavailable
        // Would need to point to a non-existent server
        print("⚠️ Server unavailable test requires test environment")
    }
}
