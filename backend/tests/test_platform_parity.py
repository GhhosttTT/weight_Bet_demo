"""跨平台高影响页面文案与业务边界的静态一致性检查。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANDROID_WITHDRAW = ROOT / "android/app/src/main/res/layout/activity_withdraw.xml"
IOS_WITHDRAW = ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewController.swift"
IOS_PLAN_DETAIL = ROOT / "ios/WeightLossBetting/UI/Plans/PlanDetailViewController.swift"


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


def test_pending_plan_creator_uses_cancel_action_on_ios():
    ios = IOS_PLAN_DETAIL.read_text(encoding="utf-8")
    pending_branch = ios[ios.index("private func showCancelOnly()"):ios.index("private func showAcceptRejectForm()")]
    assert 'cancelButton.isHidden = false' in pending_branch
    assert 'cancelButton.setTitle("撤销计划"' in pending_branch
    assert 'giveUpButton.isHidden = true' in pending_branch
