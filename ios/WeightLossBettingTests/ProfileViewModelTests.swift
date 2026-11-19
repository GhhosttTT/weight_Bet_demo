import XCTest
@testable import WeightLossBetting

/// Profile data validation tests.  Network-facing ProfileViewModel behavior is
/// covered by the backend contract/parity tests; these tests keep the mobile
/// input boundary executable instead of leaving a placeholder assertion.
class ProfileViewModelTests: XCTestCase {

    private func validRequest(
        nickname: String = "小明",
        age: Int = 30,
        height: Double = 175,
        currentWeight: Double = 80,
        targetWeight: Double? = 70
    ) -> UserUpdateRequest {
        UserUpdateRequest(
            nickname: nickname,
            gender: .male,
            age: age,
            height: height,
            currentWeight: currentWeight,
            targetWeight: targetWeight
        )
    }

    func testValidProfileRequestPassesValidation() {
        if case .failure = validRequest().validate() {
            XCTFail("有效资料不应被拒绝")
        }
    }

    func testNicknameMustHaveAtLeastTwoCharacters() {
        guard case .failure(.nicknameTooShort) = validRequest(nickname: "小").validate() else {
            return XCTFail("短昵称应被拒绝")
        }
    }

    func testAgeHeightAndWeightRangesAreEnforced() {
        guard case .failure = validRequest(age: 12).validate() else {
            return XCTFail("超出年龄范围的资料应被拒绝")
        }
        guard case .failure = validRequest(height: 99).validate() else {
            return XCTFail("超出身高范围的资料应被拒绝")
        }
        guard case .failure = validRequest(currentWeight: 29).validate() else {
            return XCTFail("超出体重范围的资料应被拒绝")
        }
    }

    func testTargetWeightIsOptionalButValidatedWhenProvided() {
        if case .failure = validRequest(targetWeight: nil).validate() {
            XCTFail("不填写目标体重应允许保存")
        }
        guard case .failure = validRequest(targetWeight: 301).validate() else {
            return XCTFail("超出范围的目标体重应被拒绝")
        }
    }
}
