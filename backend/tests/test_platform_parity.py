"""跨平台高影响页面文案与业务边界的静态一致性检查。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANDROID_WITHDRAW = ROOT / "android/app/src/main/res/layout/activity_withdraw.xml"
IOS_WITHDRAW = ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewController.swift"


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
