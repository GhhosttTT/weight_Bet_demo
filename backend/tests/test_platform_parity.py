"""跨平台高影响页面文案与业务边界的静态一致性检查。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANDROID_WITHDRAW = ROOT / "android/app/src/main/res/layout/activity_withdraw.xml"
ANDROID_CHARGE_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt"
IOS_CHARGE_VC = ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewController.swift"
IOS_WITHDRAW = ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewController.swift"
IOS_PLAN_DETAIL = ROOT / "ios/WeightLossBetting/UI/Plans/PlanDetailViewController.swift"
IOS_NETWORK_FILES = (
    ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift",
    ROOT / "ios/WeightLossBetting/Data/Network/ErrorInterceptor.swift",
)
ANDROID_API = ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt"
ANDROID_PROFILE_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/profile/ProfileViewModel.kt"
IOS_API = ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift"
IOS_PROFILE_VM = ROOT / "ios/WeightLossBetting/UI/Profile/ProfileViewModel.swift"


def test_withdrawal_copy_and_limits_match_between_mobile_platforms():
    android = ANDROID_WITHDRAW.read_text(encoding="utf-8")
    ios = IOS_WITHDRAW.read_text(encoding="utf-8")

    for text in (
        "最低提现金额",
        "¥0.01",
        "最高提现金额",
        "¥50,000",
        "设置提现账户",
        "确认提现",
    ):
        assert text in android
        assert text in ios

    assert "请输入提现金额（元）" in ios
    assert "可用余额：¥" in ios
    assert 'amount <= 50000' in ios


def test_charge_limits_match_between_mobile_platforms():
    android = ANDROID_CHARGE_VM.read_text(encoding="utf-8")
    ios = IOS_CHARGE_VC.read_text(encoding="utf-8")

    assert 'amountDouble < 0.01' in android
    assert 'amount >= 0.01' in ios
    assert 'amountDouble > 10000' in android
    assert 'amount <= 10000' in ios


def test_ios_network_logging_does_not_emit_urls_or_response_bodies():
    source = "\n".join(path.read_text(encoding="utf-8") for path in IOS_NETWORK_FILES)

    assert 'absoluteString' not in source
    assert 'Raw response' not in source
    assert 'Response Body' not in source
    assert 'Error Body' not in source


def test_pending_plan_creator_uses_cancel_action_on_ios():
    ios = IOS_PLAN_DETAIL.read_text(encoding="utf-8")
    pending_branch = ios[ios.index("private func showCancelOnly()"):ios.index("private func showAcceptRejectForm()")]
    assert 'cancelButton.isHidden = false' in pending_branch
    assert 'cancelButton.setTitle("撤销计划"' in pending_branch
    assert 'giveUpButton.isHidden = true' in pending_branch
    assert 'self?.viewModel.revokePlan()' in ios


def test_account_deletion_and_backend_logout_are_exposed_on_both_mobile_platforms():
    android_api = ANDROID_API.read_text(encoding="utf-8")
    android_vm = ANDROID_PROFILE_VM.read_text(encoding="utf-8")
    ios_api = IOS_API.read_text(encoding="utf-8")
    ios_vm = IOS_PROFILE_VM.read_text(encoding="utf-8")

    assert '@DELETE("api/users/{userId}")' in android_api
    assert 'suspend fun logout()' in android_vm
    assert 'func deleteUserAccount(userId: String' in ios_api
    assert 'func deleteAccount(completion:' in ios_vm
