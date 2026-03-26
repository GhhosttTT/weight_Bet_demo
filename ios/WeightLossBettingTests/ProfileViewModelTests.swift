import XCTest
@testable import WeightLossBetting

/// Unit tests for ProfileViewModel (Task 33.4)
class ProfileViewModelTests: XCTestCase {
    
    var sut: ProfileViewModel!
    var mockRepository: MockUserRepository!
    
    override func setUp() {
        super.setUp()
        mockRepository = MockUserRepository()
        sut = ProfileViewModel(repository: mockRepository)
    }
    
    override func tearDown() {
        sut = nil
        mockRepository = nil
        super.tearDown()
    }
    
    // MARK: - Load User Profile Tests
    
    func testLoadUserProfile_Success() {
        // Given
        let expectedUser = User(
            id: "user123",
            email: "test@example.com",
            nickname: "TestUser",
            gender: .male,
            age: 25,
            height: 175.0,
            currentWeight: 70.0,
            targetWeight: 65.0,
            paymentMethod: nil
        )
        mockRepository.userToReturn = expectedUser
        
        let expectation = self.expectation(description: "Load user profile")
        var resultUser: User?
        
        // When
        sut.loadUserProfile { result in
            if case .success(let user) = result {
                resultUser = user
            }
            expectation.fulfill()
        }
        
        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertNotNil(resultUser)
        XCTAssertEqual(resultUser?.id, expectedUser.id)
        XCTAssertEqual(resultUser?.email, expectedUser.email)
        XCTAssertEqual(resultUser?.nickname, expectedUser.nickname)
    }
    
    func testLoadUserProfile_Failure() {
        // Given
        mockRepository.shouldFail = true
        let expectation = self.expectation(description: "Load user profile failure")
        var resultError: Error?
        
        // When
        sut.loadUserProfile { result in
            if case .failure(let error) = result {
                resultError = error
            }
            expectation.fulfill()
        }
        
        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertNotNil(resultError)
    }
    
    // MARK: - Update User Profile Tests
    
    func testUpdateProfile_ValidData_Success() {
        // Given
        let updateData = UserUpdateRequest(
            nickname: "NewNickname",
            gender: .female,
            age: 30,
            height: 165.0,
            currentWeight: 60.0,
            targetWeight: 55.0
        )
        
        let expectation = self.expectation(description: "Update profile")
        var updateSuccess = false
        
        // When
        sut.updateProfile(updateData) { result in
            if case .success = result {
                updateSuccess = true
            }
            expectation.fulfill()
        }
        
        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertTrue(updateSuccess)
    }
    
    func testUpdateProfile_InvalidAge_Failure() {
        // Given
        let updateData = UserUpdateRequest(
            nickname: "TestUser",
            gender: .male,
            age: 10, // Invalid: < 13
            height: 175.0,
            currentWeight: 70.0,
            targetWeight: 65.0
        )
        
        let expectation = self.expectation(description: "Update profile with invalid age")
        var validationError: Error?
        
        // When
        sut.updateProfile(updateData) { result in
            if case .failure(let error) = result {
                validationError = error
            }
            expectation.fulfill()
        }
        
        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertNotNil(validationError)
    }
    
    func testUpdateProfile_InvalidHeight_Failure() {
        // Given
        let updateData = UserUpdateRequest(
            nickname: "TestUser",
            gender: .male,
            age: 25,
            height: 90.0, // Invalid: < 100
            currentWeight: 70.0,
            targetWeight: 65.0
        )
        
        let expectation = self.expectation(description: "Update profile with invalid height")
        var validationError: Error?
        
        // When
        sut.updateProfile(updateData) { result in
            if case .failure(let error) = result {
                validationError = error
            }
            expectation.fulfill()
        }
        
        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertNotNil(validationError)
    }
    
    func testUpdateProfile_InvalidWeight_Failure() {
        // Given
        let updateData = UserUpdateRequest(
            nickname: "TestUser",
            gender: .male,
            age: 25,
            height: 175.0,
            currentWeight: 25.0, // Invalid: < 30
            targetWeight: 65.0
        )
        
        let expectation = self.expectation(description: "Update profile with invalid weight")
        var validationError: Error?
        
        // When
        sut.updateProfile(updateData) { result in
            if case .failure(let error) = result {
                validationError = error
            }
            expectation.fulfill()
        }
        
        // Then
        waitForExpectations(timeout: 1.0)
        XCTAssertNotNil(validationError)
    }
    
    // MARK: - Validation Tests
    
    func testValidateAge_ValidRange() {
        XCTAssertTrue(sut.validateAge(13))
        XCTAssertTrue(sut.validateAge(25))
        XCTAssertTrue(sut.validateAge(120))
    }
    
    func testValidateAge_InvalidRange() {
        XCTAssertFalse(sut.validateAge(12))
        XCTAssertFalse(sut.validateAge(121))
        XCTAssertFalse(sut.validateAge(0))
    }
    
    func testValidateHeight_ValidRange() {
        XCTAssertTrue(sut.validateHeight(100.0))
        XCTAssertTrue(sut.validateHeight(175.0))
        XCTAssertTrue(sut.validateHeight(250.0))
    }
    
    func testValidateHeight_InvalidRange() {
        XCTAssertFalse(sut.validateHeight(99.9))
        XCTAssertFalse(sut.validateHeight(250.1))
        XCTAssertFalse(sut.validateHeight(0.0))
    }
    
    func testValidateWeight_ValidRange() {
        XCTAssertTrue(sut.validateWeight(30.0))
        XCTAssertTrue(sut.validateWeight(70.0))
        XCTAssertTrue(sut.validateWeight(300.0))
    }
    
    func testValidateWeight_InvalidRange() {
        XCTAssertFalse(sut.validateWeight(29.9))
        XCTAssertFalse(sut.validateWeight(300.1))
        XCTAssertFalse(sut.validateWeight(0.0))
    }
}

// MARK: - Mock Repository

class MockUserRepository: UserRepositoryProtocol {
    var userToReturn: User?
    var shouldFail = false
    var error = NSError(domain: "TestError", code: -1, userInfo: nil)
    
    func getUser(userId: String, completion: @escaping (Result<User, Error>) -> Void) {
        if shouldFail {
            completion(.failure(error))
        } else if let user = userToReturn {
            completion(.success(user))
        } else {
            completion(.failure(error))
        }
    }
    
    func updateUser(userId: String, updateData: UserUpdateRequest, completion: @escaping (Result<User, Error>) -> Void) {
        if shouldFail {
            completion(.failure(error))
        } else if let user = userToReturn {
            completion(.success(user))
        } else {
            completion(.failure(error))
        }
    }
}
