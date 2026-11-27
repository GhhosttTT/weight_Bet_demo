"""跨平台高影响页面文案与业务边界的静态一致性检查。"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
ANDROID_WITHDRAW = ROOT / "android/app/src/main/res/layout/activity_withdraw.xml"
ANDROID_CHARGE_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt"
ANDROID_CHARGE_ACTIVITY = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeActivity.kt"
ANDROID_CREATE_PLAN = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/CreatePlanActivity.kt"
ANDROID_CREATE_PLAN_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/CreatePlanViewModel.kt"
ANDROID_CREATE_PLAN_MODEL = ROOT / "android/app/src/main/java/com/weightloss/betting/data/model/Models.kt"
ANDROID_INVITE_DIALOG = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/InviteFriendDialog.kt"
IOS_CHARGE_VC = ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewController.swift"
IOS_CHARGE_VM = ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift"
IOS_WITHDRAW = ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewController.swift"
IOS_PLAN_DETAIL = ROOT / "ios/WeightLossBetting/UI/Plans/PlanDetailViewController.swift"
IOS_CHECK_IN_VM = ROOT / "ios/WeightLossBetting/UI/CheckIn/CheckInViewModel.swift"
IOS_CHECK_IN_VC = ROOT / "ios/WeightLossBetting/UI/CheckIn/CheckInViewController.swift"
ANDROID_CHECK_IN_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/checkin/CheckInViewModel.kt"
ANDROID_CHECK_IN_ACTIVITY = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/checkin/CheckInActivity.kt"
IOS_MAIN = ROOT / "ios/WeightLossBetting/UI/Main/MainTabBarController.swift"
ANDROID_HOME_LAYOUT = ROOT / "android/app/src/main/res/layout/fragment_home.xml"
IOS_PODFILE = ROOT / "ios/Podfile"
IOS_PODFILE_LOCK = ROOT / "ios/Podfile.lock"
IOS_NETWORK_FILES = (
    ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift",
    ROOT / "ios/WeightLossBetting/Data/Network/ErrorInterceptor.swift",
)
ANDROID_API = ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt"
ANDROID_PROFILE_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/profile/ProfileViewModel.kt"
IOS_API = ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift"
IOS_PROFILE_VM = ROOT / "ios/WeightLossBetting/UI/Profile/ProfileViewModel.swift"
ANDROID_MAIN = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/MainActivity.kt"
ANDROID_NOTIFICATION_HELPER = ROOT / "android/app/src/main/java/com/weightloss/betting/util/NotificationPermissionHelper.kt"
IOS_PENDING_ACTIONS = ROOT / "ios/WeightLossBetting/Data/Service/PendingActionsService.swift"
ANDROID_LOGIN = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/auth/LoginActivity.kt"
ANDROID_LOGIN_STRINGS = ROOT / "android/app/src/main/res/values/strings.xml"
IOS_LOGIN = ROOT / "ios/WeightLossBetting/UI/Auth/LoginViewController.swift"
IOS_APP_DELEGATE = ROOT / "ios/WeightLossBetting/AppDelegate.swift"
IOS_INFO_PLIST = ROOT / "ios/WeightLossBetting/Info.plist"
ANDROID_COACH_VM = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/main/CoachViewModel.kt"
IOS_COACH_VM = ROOT / "ios/WeightLossBetting/UI/Main/CoachViewModel.swift"
ANDROID_COACH_FRAGMENT = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/main/CoachFragment.kt"
ANDROID_COACH_LAYOUT = ROOT / "android/app/src/main/res/layout/fragment_coach.xml"
ANDROID_BOTTOM_NAV = ROOT / "android/app/src/main/res/menu/bottom_navigation_menu.xml"
ANDROID_PAYMENT_API = ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt"
ANDROID_PAYMENT_REPOSITORY = ROOT / "android/app/src/main/java/com/weightloss/betting/data/repository/PaymentRepository.kt"
IOS_PAYMENT_API = ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift"
IOS_PAYMENT_REPOSITORY = ROOT / "ios/WeightLossBetting/Data/Repository/PaymentRepository.swift"
IOS_MODELS = ROOT / "ios/WeightLossBetting/Data/Model/Models.swift"
IOS_BALANCE_VC = ROOT / "ios/WeightLossBetting/UI/Payment/BalanceViewController.swift"
IOS_PAYMENT_METHOD_VC = ROOT / "ios/WeightLossBetting/UI/Profile/PaymentMethodViewController.swift"
IOS_PAYMENT_METHOD_VM = ROOT / "ios/WeightLossBetting/UI/Profile/PaymentMethodViewModel.swift"
ANDROID_REGISTER = ROOT / "android/app/src/main/res/layout/activity_register.xml"
ANDROID_EDIT_PROFILE = ROOT / "android/app/src/main/res/layout/activity_edit_profile.xml"
IOS_REGISTER = ROOT / "ios/WeightLossBetting/UI/Auth/RegisterViewController.swift"
IOS_EDIT_PROFILE = ROOT / "ios/WeightLossBetting/UI/Profile/EditProfileViewController.swift"
ANDROID_PLAN_ADAPTER = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/PlanAdapter.kt"
IOS_PLANS = ROOT / "ios/WeightLossBetting/UI/Plans/PlansViewController.swift"
ANDROID_TRANSACTION_ADAPTER = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/TransactionAdapter.kt"
IOS_BALANCE = ROOT / "ios/WeightLossBetting/UI/Payment/BalanceViewController.swift"
ANDROID_LOGIN_LAYOUT = ROOT / "android/app/src/main/res/layout/activity_login.xml"
ANDROID_PROFILE_LAYOUT = ROOT / "android/app/src/main/res/layout/fragment_profile.xml"
ANDROID_PROFILE_FRAGMENT = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/profile/ProfileFragment.kt"
IOS_PROFILE = ROOT / "ios/WeightLossBetting/UI/Profile/ProfileViewController.swift"
ANDROID_PLAN_DETAIL = ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/PlanDetailActivity.kt"
ANDROID_BACKUP_RULES = ROOT / "android/app/src/main/res/xml/backup_rules.xml"
ANDROID_DATA_EXTRACTION_RULES = ROOT / "android/app/src/main/res/xml/data_extraction_rules.xml"
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

    # 两端提现页都要展示可用余额，并提供同一组快捷金额。
    assert 'tvAvailableBalance' in android
    assert 'availableBalanceLabel' in ios
    for amount in ("50", "100", "200", "500"):
        assert f'¥{amount}' in android
        assert f'{amount}.0' in ios

    assert "请输入提现金额（元）" in ios
    assert "可用余额：¥" in ios
    assert 'amount <= 50000' in ios


def test_android_backup_rules_exclude_authentication_and_pending_payment_state():
    backup = ANDROID_BACKUP_RULES.read_text(encoding="utf-8")
    extraction = ANDROID_DATA_EXTRACTION_RULES.read_text(encoding="utf-8")
    expected = 'domain="file" path="datastore/auth_prefs.preferences_pb"'

    assert expected in backup
    assert extraction.count(expected) == 2
    assert "<device-transfer>" in extraction


def test_ios_pod_lock_matches_google_and_stripe_dependencies():
    podfile = IOS_PODFILE.read_text(encoding="utf-8")
    lock = IOS_PODFILE_LOCK.read_text(encoding="utf-8")

    assert "pod 'GoogleSignIn', '~> 9.0'" in podfile
    assert "GoogleSignIn (~> 9.0)" in lock
    assert "GoogleSignIn (9.2.0)" in lock
    assert "pod 'StripePaymentSheet', '~> 23.5'" in podfile
    assert "StripePaymentSheet (~> 23.5)" in lock
    assert "StripePaymentSheet (23.32.0)" in lock
    assert "COCOAPODS: 1.17.0" in lock


def test_charge_limits_match_between_mobile_platforms():
    android = ANDROID_CHARGE_VM.read_text(encoding="utf-8")
    ios = IOS_CHARGE_VC.read_text(encoding="utf-8")

    assert 'amountDouble < 0.01' in android
    assert 'amount >= 0.01' in ios
    assert 'amountDouble > 10000' in android
    assert 'amount <= 10000' in ios


def test_charge_flow_uses_stripe_payment_sheet_and_webhook_entrypoint_on_both_platforms():
    android_vm = ANDROID_CHARGE_VM.read_text(encoding="utf-8")
    android_activity = ANDROID_CHARGE_ACTIVITY.read_text(encoding="utf-8")
    ios_vm = IOS_CHARGE_VM.read_text(encoding="utf-8")
    ios_controller = IOS_CHARGE_VC.read_text(encoding="utf-8")

    # 两端都必须先创建 PaymentIntent，再由 Stripe SDK 收集/确认卡信息。
    assert "createChargeIntent" in android_vm
    assert "createChargeIntent" in ios_vm
    assert "presentWithPaymentIntent" in android_activity
    assert "PaymentSheet(" in ios_controller
    assert "paymentIntentClientSecret" in ios_controller

    # 客户端完成支付后只能等待服务端 webhook 入账，不能调用旧的 demo 充值接口。
    assert "paymentCompleted(state.transactionId)" in android_activity
    assert "paymentCompleted()" in ios_controller
    assert "AwaitingWebhook" in android_vm
    assert ".awaitingWebhook" in ios_vm
    assert "api/payments/charge" not in android_vm
    assert "api/payments/charge" not in ios_vm
    assert "charge_funds" not in android_vm + ios_vm


def test_create_plan_invitation_flow_matches_ios_pre_create_sequence():
    android_activity = ANDROID_CREATE_PLAN.read_text(encoding="utf-8")
    android_vm = ANDROID_CREATE_PLAN_VM.read_text(encoding="utf-8")
    android_model = ANDROID_CREATE_PLAN_MODEL.read_text(encoding="utf-8")
    invite_dialog = ANDROID_INVITE_DIALOG.read_text(encoding="utf-8")
    ios_create = (ROOT / "ios/WeightLossBetting/UI/Plans/CreatePlanViewController.swift").read_text(encoding="utf-8")

    # Android must select the invitee before sending create-plan, like iOS.
    assert "newInstanceForPreCreate" in android_activity
    assert "setFragmentResultListener" in android_activity
    assert "inviteeId = pendingInviteeId" in android_activity
    assert 'SerializedName("invitee_id")' in android_model
    assert "inviteeId: String? = null" in android_vm
    assert "ARG_PRE_CREATE" in invite_dialog
    assert "RESULT_PRE_CREATE_INVITE" in invite_dialog
    assert "showInvitePage" in ios_create


def test_ios_network_logging_does_not_emit_urls_or_response_bodies():
    source = "\n".join(path.read_text(encoding="utf-8") for path in IOS_NETWORK_FILES)

    assert 'absoluteString' not in source
    assert 'Raw response' not in source
    assert 'Response Body' not in source
    assert 'Error Body' not in source


def test_pending_plan_creator_uses_cancel_action_on_ios():
    ios = IOS_PLAN_DETAIL.read_text(encoding="utf-8")
    pending_branch = ios[ios.index("private func showCancelOnly(showInvite:"):ios.index("private func showAcceptRejectForm()")]
    assert 'cancelButton.isHidden = false' in pending_branch
    assert 'cancelButton.setTitle("撤销计划"' in pending_branch
    assert 'giveUpButton.isHidden = true' in pending_branch
    assert pending_branch.count('inviteButton.isHidden') == 1
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


def test_pending_actions_refresh_when_both_platforms_return_to_foreground():
    android = ANDROID_MAIN.read_text(encoding="utf-8")
    ios = IOS_PENDING_ACTIONS.read_text(encoding="utf-8")

    assert "override fun onResume()" in android
    assert "checkPendingActions()" in android
    assert "func checkAndHandlePendingActions()" in ios
    assert "waitForModalDismiss" in ios


def test_matched_settlement_state_copy_matches_on_both_mobile_platforms():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/settlement/SettlementActivity.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Settlement/SettlementViewController.swift").read_text(encoding="utf-8")
    expected = "双方选择已匹配，等待系统结算"
    assert expected in android
    assert expected in ios


def test_notification_permission_is_requested_once_on_android_like_ios_login_flow():
    android = ANDROID_MAIN.read_text(encoding="utf-8")
    helper = ANDROID_NOTIFICATION_HELPER.read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Auth/LoginViewController.swift").read_text(encoding="utf-8")

    assert "requestNotificationPermissionIfNeeded()" in android
    assert "PREF_NOTIFICATION_PERMISSION_REQUESTED" in android
    assert "hasNotificationPermission" in android
    assert "requestNotificationPermission" in helper
    assert "requestNotificationPermissionsIfNeeded" in ios


def test_dispute_update_notifications_navigate_to_settlement_on_both_mobile_platforms():
    android = ANDROID_MAIN.read_text(encoding="utf-8")
    android_fcm = (ROOT / "android/app/src/main/java/com/weightloss/betting/service/FCMService.kt").read_text(encoding="utf-8")
    ios_service = (ROOT / "ios/WeightLossBetting/Data/Service/NotificationService.swift").read_text(encoding="utf-8")
    ios_coordinator = (ROOT / "ios/WeightLossBetting/UI/Common/NotificationNavigationCoordinator.swift").read_text(encoding="utf-8")
    ios_tab = (ROOT / "ios/WeightLossBetting/UI/Main/MainTabBarController.swift").read_text(encoding="utf-8")
    ios_settlement = (ROOT / "ios/WeightLossBetting/UI/Settlement/SettlementViewController.swift").read_text(encoding="utf-8")

    assert '"settlement", "dispute_updated"' in android
    assert "related_id" in android_fcm
    assert 'case "settlement", "dispute_updated"' in ios_service
    assert 'case "settlement", "dispute_updated"' in ios_coordinator
    assert '"settlement", "dispute_updated"' in ios_tab
    assert "SettlementViewController(" in ios_tab
    assert "getSettlementSelectionStatus(planId: planId)" in ios_settlement


def test_charge_amount_validation_matches_on_android_and_ios():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")

    for content in (android, ios):
        assert "0.01" in content
        assert "10000" in content
        assert "充值金额必须大于0" in content
        assert "充值金额不能少于0.01元" in content
        assert "单次充值金额不能超过10000元" in content
    assert "amount.isFinite" in ios
    assert "amountDouble <= 0" in android


def test_withdraw_amount_validation_matches_on_android_and_ios():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/WithdrawViewModel.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewModel.swift").read_text(encoding="utf-8")

    for content in (android, ios):
        assert "0.01" in content
        assert "50000" in content
        assert "提现金额必须大于0" in content
        assert "提现金额不能少于0.01元" in content
        assert "单次提现金额不能超过50000元" in content
    assert "amount.isFinite" in ios
    assert "amountDouble <= 0" in android


def test_google_login_configuration_state_matches_between_mobile_platforms():
    android = ANDROID_LOGIN.read_text(encoding="utf-8")
    android_strings = ANDROID_LOGIN_STRINGS.read_text(encoding="utf-8")
    ios = IOS_LOGIN.read_text(encoding="utf-8")
    ios_delegate = IOS_APP_DELEGATE.read_text(encoding="utf-8")
    ios_plist = IOS_INFO_PLIST.read_text(encoding="utf-8")

    assert "updateGoogleSignInAvailability()" in android
    assert 'binding.btnGoogleLogin.isEnabled = googleSignInConfigured' in android
    assert "Google 登录未配置" in android
    assert "default_web_client_id" in android_strings
    assert "updateGoogleSignInAvailability()" in ios
    assert "googleSignInButton.isEnabled = configured" in ios
    assert "Google 登录未配置" in ios
    assert "configureGoogleSignIn()" in ios_delegate
    assert "GIDConfiguration(clientID: clientID)" in ios_delegate
    assert "GIDClientID" in ios_plist
    assert "hasCallbackScheme" in ios_delegate
    assert "expectedReversedClientID" in ios_delegate
    assert "value == expectedScheme" in ios_delegate
    assert "GoogleSignInConfiguration.isConfigured" in ios


def test_android_google_login_uses_credential_manager_nonce_and_snake_case_payload():
    android = ANDROID_LOGIN.read_text(encoding="utf-8")
    models = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/model/Models.kt").read_text(encoding="utf-8")
    repository = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/repository/AuthRepository.kt").read_text(encoding="utf-8")

    assert "CredentialManager" in android
    assert "GetGoogleIdOption.Builder()" in android
    assert ".setNonce(nonce)" in android
    assert "GoogleIdTokenCredential.createFrom" in android
    assert '@SerializedName("id_token")' in models
    assert "val nonce: String" in models
    assert "googleLogin(idToken: String, nonce: String)" in repository


def test_ios_google_login_sends_custom_nonce_to_backend():
    login_vm = (ROOT / "ios/WeightLossBetting/UI/Auth/LoginViewModel.swift").read_text(encoding="utf-8")
    repository = (ROOT / "ios/WeightLossBetting/Data/Repository/AuthRepository.swift").read_text(encoding="utf-8")
    api = (ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift").read_text(encoding="utf-8")
    podfile = (ROOT / "ios/Podfile").read_text(encoding="utf-8")

    assert "nonce: nonce" in login_vm
    assert "googleLogin(idToken: idToken, nonce: nonce)" in login_vm
    assert "func googleLogin(idToken: String, nonce: String," in repository
    assert "func googleLogin(idToken: String, nonce: String," in api
    assert '"nonce": nonce' in api
    assert "pod 'GoogleSignIn', '~> 9.0'" in podfile


def test_payment_failure_resets_idempotency_key_on_both_mobile_platforms():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")

    android_failure = android.split("fun paymentFailed", 1)[1].split("}", 1)[0]
    ios_failure = ios.split("func paymentFailed", 1)[1].split("}", 1)[0]
    assert "chargeIdempotencyKey = null" in android_failure
    assert "chargeIdempotencyKey = nil" in ios_failure


def test_payment_cancel_keeps_recovery_order_but_resets_new_charge_key():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")

    android_cancel = android.split("fun paymentCanceled", 1)[1].split("}", 1)[0]
    ios_cancel = ios.split("func paymentCanceled", 1)[1].split("}", 1)[0]
    assert "chargeIdempotencyKey = null" in android_cancel
    assert "chargeIdempotencyKey = nil" in ios_cancel
    assert "clearPendingCharge" not in android_cancel
    assert "removeObject(forKey: \"pendingChargeTransactionId\")" not in ios_cancel


def test_payment_success_waits_for_webhook_status_on_both_mobile_platforms():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt").read_text(encoding="utf-8")
    android_api = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")
    ios_api = (ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift").read_text(encoding="utf-8")

    assert "AwaitingWebhook" in android
    assert "getTransactionStatus(transactionId)" in android
    assert 'api/payments/transactions/{transactionId}' in android_api
    assert ".awaitingWebhook" in ios
    assert "getTransactionStatus(transactionId: transactionId)" in ios
    assert "/payments/transactions/\\(transactionId)" in ios_api


def test_interrupted_charge_can_request_a_resume_intent_on_both_mobile_platforms():
    android_api = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt").read_text(encoding="utf-8")
    android_repository = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/repository/PaymentRepository.kt").read_text(encoding="utf-8")
    ios_api = (ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift").read_text(encoding="utf-8")
    ios_repository = (ROOT / "ios/WeightLossBetting/Data/Repository/PaymentRepository.swift").read_text(encoding="utf-8")

    assert 'api/payments/transactions/{transactionId}/resume' in android_api
    assert "resumeChargeIntent(transactionId: String)" in android_repository
    assert "/payments/transactions/\\(transactionId)/resume" in ios_api
    assert "resumeChargeIntent(transactionId: String)" in ios_repository


def test_interrupted_charge_is_persisted_and_restored_on_both_mobile_platforms():
    android_vm = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt").read_text(encoding="utf-8")
    android_activity = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeActivity.kt").read_text(encoding="utf-8")
    token_manager = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/TokenManager.kt").read_text(encoding="utf-8")
    ios_vm = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")
    ios_controller = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewController.swift").read_text(encoding="utf-8")

    assert "savePendingCharge(result.data.transactionId)" in android_vm
    assert "restorePendingCharge()" in android_activity
    assert "pending_charge_transaction_id" in token_manager
    assert "getPendingCharge()" in ios_vm
    assert "savePendingCharge(intent.transactionId)" in ios_vm
    assert "clearPendingCharge()" in ios_vm
    assert "restorePendingCharge()" in ios_controller


def test_ios_sensitive_offline_identity_and_payment_recovery_use_keychain():
    offline_sync = (ROOT / "ios/WeightLossBetting/Data/Local/OfflineSyncManager.swift").read_text(encoding="utf-8")
    charge_vm = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")
    token_manager = (ROOT / "ios/WeightLossBetting/Data/Network/TokenManager.swift").read_text(encoding="utf-8")
    auth = (ROOT / "ios/WeightLossBetting/Data/Repository/AuthRepository.swift").read_text(encoding="utf-8")

    assert "AuthRepository.shared.getCurrentUserId()" in offline_sync
    assert "savePendingCharge" in token_manager
    assert "getPendingCharge" in token_manager
    assert "clearPendingCharge" in token_manager
    assert 'UserDefaults.standard.set(intent.transactionId' not in charge_vm
    assert 'UserDefaults.standard.removeObject(forKey: "pendingChargeTransactionId")' in charge_vm
    assert "TokenManager.shared.clearPendingCharge()" in auth


def test_withdraw_response_mapping_keeps_transaction_and_status_fields():
    android_models = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/model/Models.kt").read_text(encoding="utf-8")
    ios_models = (ROOT / "ios/WeightLossBetting/Data/Model/Models.swift").read_text(encoding="utf-8")

    assert '@SerializedName("transaction_id") val transactionId' in android_models
    assert "val status: String? = null" in android_models
    assert 'case transactionId = "transaction_id"' in ios_models


def test_ios_balance_uses_authenticated_user_id():
    balance_vm = (ROOT / "ios/WeightLossBetting/UI/Payment/BalanceViewModel.swift").read_text(encoding="utf-8")

    assert "AuthRepository.shared.getCurrentUserId()" in balance_vm
    assert 'userId: "123"' not in balance_vm


def test_ios_cached_plan_lookup_uses_plan_id_without_empty_user_scope():
    cache = (ROOT / "ios/WeightLossBetting/Data/Local/CacheManager.swift").read_text(encoding="utf-8")
    core_data = (ROOT / "ios/WeightLossBetting/Data/Local/CoreDataManager.swift").read_text(encoding="utf-8")

    assert "coreDataManager.getCachedBettingPlan(id: id)" in cache
    assert "func getCachedBettingPlan(id: String) -> BettingPlan?" in core_data
    assert 'getCachedBettingPlans(userId: "")' not in cache


def test_registration_password_minimum_matches_backend_and_android():
    ios_vm = (ROOT / "ios/WeightLossBetting/UI/Auth/RegisterViewModel.swift").read_text(encoding="utf-8")
    ios_error = (ROOT / "ios/WeightLossBetting/Data/Model/ValidationError.swift").read_text(encoding="utf-8")
    android_vm = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/auth/RegisterViewModel.kt").read_text(encoding="utf-8")
    backend_schema = (ROOT / "backend/app/schemas/user.py").read_text(encoding="utf-8")

    assert "password.count >= 8" in ios_vm
    assert "密码至少需要8个字符" in ios_error
    assert "password.length < 8" in android_vm
    assert "min_length=8" in backend_schema


def test_registration_profile_validation_matches_between_mobile_platforms():
    ios = (ROOT / "ios/WeightLossBetting/UI/Auth/RegisterViewModel.swift").read_text(encoding="utf-8")
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/auth/RegisterViewModel.kt").read_text(encoding="utf-8")

    assert "nickname.count <= 20" in ios
    assert "age >= 13 && age <= 120" in ios
    assert "height.isFinite && height >= 100 && height <= 250" in ios
    assert "currentWeight.isFinite && currentWeight >= 30 && currentWeight <= 300" in ios
    assert "nickname.length > 20" in android
    assert "age < 13 || age > 120" in android
    assert "height < 100 || height > 250" in android
    assert "currentWeight < 30 || currentWeight > 300" in android


def test_plan_bet_minimum_validation_matches_between_mobile_platforms():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/CreatePlanViewModel.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Plans/CreatePlanViewModel.swift").read_text(encoding="utf-8")

    assert "betAmountDouble < 0.01" in android
    assert "betAmountDouble.isFinite()" in android
    assert "betAmountValue >= 0.01" in ios
    assert "betAmountValue.isFinite" in ios
    assert "赌金不能少于0.01元" in android
    assert "赌金不能少于0.01元" in ios


def test_numeric_input_validation_rejects_non_finite_values_on_both_platforms():
    android_files = [
        ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt",
        ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/WithdrawViewModel.kt",
        ROOT / "android/app/src/main/java/com/weightloss/betting/ui/checkin/CheckInViewModel.kt",
        ROOT / "android/app/src/main/java/com/weightloss/betting/ui/plan/PlanDetailViewModel.kt",
        ROOT / "android/app/src/main/java/com/weightloss/betting/ui/profile/EditProfileViewModel.kt",
    ]
    ios_files = [
        ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift",
        ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewModel.swift",
        ROOT / "ios/WeightLossBetting/UI/CheckIn/CheckInViewModel.swift",
        ROOT / "ios/WeightLossBetting/UI/Plans/PlanDetailViewModel.swift",
        ROOT / "ios/WeightLossBetting/UI/Profile/EditProfileViewModel.swift",
    ]

    for path in android_files:
        assert ".isFinite()" in path.read_text(encoding="utf-8"), path
    for path in ios_files:
        assert ".isFinite" in path.read_text(encoding="utf-8"), path


def test_check_in_without_plan_id_targets_all_active_plans_on_both_platforms():
    ios_vm = IOS_CHECK_IN_VM.read_text(encoding="utf-8")
    ios_vc = IOS_CHECK_IN_VC.read_text(encoding="utf-8")
    android_vm = ANDROID_CHECK_IN_VM.read_text(encoding="utf-8")
    android_activity = ANDROID_CHECK_IN_ACTIVITY.read_text(encoding="utf-8")

    assert "createCheckInForAllActivePlans" in ios_vm
    assert 'status: "active"' in ios_vm
    assert "let activePlans = plans.filter { $0.status == .active }" in ios_vm
    assert "if planId.isEmpty" in ios_vc
    assert "createCheckInForAllPlans" in android_vm
    assert 'getUserPlans(userId, "active", forceRefresh = true)' in android_vm
    assert "if (planId == null)" in android_activity


def test_home_dashboard_visual_hierarchy_matches_between_mobile_platforms():
    ios = IOS_MAIN.read_text(encoding="utf-8")
    android = ANDROID_HOME_LAYOUT.read_text(encoding="utf-8")

    assert 'label.text = "计划概览"' in ios
    assert "QuickActionStyle" in ios
    assert '.primary),\n            ("我的计划"' in ios
    assert '.outline),\n            ("每日打卡"' in ios
    assert '.accent)' in ios
    assert 'android:text="计划概览"' in android
    assert 'android:text="创建计划&#10;发起新的减肥挑战"' in android
    assert 'android:text="我的计划&#10;查看所有对赌计划"' in android
    assert 'android:text="每日打卡&#10;记录今天的体重"' in android


def test_ios_user_identity_prefers_keychain_backed_token_manager():
    auth = (ROOT / "ios/WeightLossBetting/Data/Repository/AuthRepository.swift").read_text(encoding="utf-8")
    token_manager = (ROOT / "ios/WeightLossBetting/Data/Network/TokenManager.swift").read_text(encoding="utf-8")
    main = (ROOT / "ios/WeightLossBetting/UI/Main/MainTabBarController.swift").read_text(encoding="utf-8")
    check_in = (ROOT / "ios/WeightLossBetting/Data/Repository/CheckInRepository.swift").read_text(encoding="utf-8")

    assert "TokenManager.shared.saveUserId(userId)" in auth
    assert "return TokenManager.shared.getUserId()" in auth
    assert "TokenManager.shared.clearUserId()" in auth
    assert "func clearUserId()" in token_manager
    assert 'UserDefaults.standard.string(forKey: "currentUserId")' not in main
    assert 'UserDefaults.standard.string(forKey: "currentUserId")' not in check_in


def test_balance_transaction_history_default_page_size_matches_ios_and_backend():
    android_repo = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/repository/UserRepository.kt").read_text(encoding="utf-8")
    android_activity = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/BalanceActivity.kt").read_text(encoding="utf-8")
    payments_api = (ROOT / "backend/app/api/payments.py").read_text(encoding="utf-8")

    assert "limit: Int = 50" in android_repo
    assert "viewModel.loadTransactions(userId!!" in android_activity
    assert "limit: int = Query(default=50" in payments_api


def test_coach_initial_load_can_fetch_when_mobile_cache_is_empty():
    android = ANDROID_COACH_VM.read_text(encoding="utf-8")
    ios = IOS_COACH_VM.read_text(encoding="utf-8")

    assert "viewModelScope.launch" in android
    assert "getRecommendation(useCache = true)" in android
    assert "NetworkResult.Success" in android
    assert "NetworkResult.Error" in android
    assert "getRecommendation(useCache: useCache" in ios
    assert "cacheRecommendation(result.data)" in (ROOT / "android/app/src/main/java/com/weightloss/betting/data/repository/RecommendationRepository.kt").read_text(encoding="utf-8")


def test_coach_error_state_uses_the_same_placeholder_copy_on_both_platforms():
    android = ANDROID_COACH_FRAGMENT.read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Main/CoachViewController.swift").read_text(encoding="utf-8")

    assert 'binding.tvEmptyMessage.text = "AI 推荐服务正在启动中\\n请稍后刷新页面"' in android
    assert 'createPlaceholderLabel(text: "AI 推荐服务正在启动中\\n请稍后刷新页面")' in ios


def test_coach_semantic_colors_use_the_shared_brand_palette():
    android = ANDROID_COACH_LAYOUT.read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Main/CoachViewController.swift").read_text(encoding="utf-8")

    assert 'android:textColor="@color/brand_accent"' in android
    assert 'android:textColor="@color/brand_primary"' in android
    assert "textColor = AppTheme.Colors.accent" in ios
    assert "textColor = AppTheme.Colors.primary" in ios


def test_bottom_navigation_uses_matching_semantic_icons_on_both_platforms():
    android = ANDROID_BOTTOM_NAV.read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Main/MainTabBarController.swift").read_text(encoding="utf-8")

    for icon in ("ic_nav_home", "ic_nav_coach", "ic_nav_plans", "ic_nav_profile"):
        assert f'android:icon="@drawable/{icon}"' in android
    for icon in ('"house"', '"heart.fill"', '"list.bullet"', '"person"'):
        assert icon in ios


def test_mobile_payment_data_layers_expose_only_payment_intent_for_charges():
    android_api = ANDROID_PAYMENT_API.read_text(encoding="utf-8")
    android_repository = ANDROID_PAYMENT_REPOSITORY.read_text(encoding="utf-8")
    ios_api = IOS_PAYMENT_API.read_text(encoding="utf-8")
    ios_repository = IOS_PAYMENT_REPOSITORY.read_text(encoding="utf-8")

    assert '"api/payments/charge"' not in android_api
    assert "suspend fun createChargeIntent" in android_api
    assert "suspend fun charge(" not in android_repository
    assert "/payments/charge\"" not in ios_api
    assert "createChargeIntent(amount:" in ios_api
    assert "func charge(amount:" not in ios_repository


def test_ios_transaction_model_can_decode_backend_charge_records():
    ios_models = IOS_MODELS.read_text(encoding="utf-8")
    ios_balance = IOS_BALANCE_VC.read_text(encoding="utf-8")
    assert "enum TransactionType: String, Codable" in ios_models
    assert "case charge" in ios_models
    assert "case .charge:" in ios_balance
    assert "transaction.type == .charge" in ios_balance


def test_payment_method_page_uses_matching_stripe_secure_setup_on_both_platforms():
    android = (ROOT / "android/app/src/main/res/layout/activity_payment_method.xml").read_text(encoding="utf-8")
    android_activity = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/profile/PaymentMethodActivity.kt").read_text(encoding="utf-8")
    android_api = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt").read_text(encoding="utf-8")
    ios = IOS_PAYMENT_METHOD_VC.read_text(encoding="utf-8")
    ios_vm = IOS_PAYMENT_METHOD_VM.read_text(encoding="utf-8")
    ios_api = (ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift").read_text(encoding="utf-8")
    for text in ("绑定支付方式", "Stripe 安全", "不会读取或保存完整银行卡号"):
        assert text in android
        assert text in ios
    assert "setup-intent" in android_api
    assert "presentWithSetupIntent" in android_activity
    assert "createSetupIntent" in ios_api
    assert "setupIntentClientSecret" in ios
    assert "etCardNumber" not in android
    assert "cardNumberTextField" not in ios
    assert "请输入有效的银行卡号" not in ios_vm


def test_payment_method_page_uses_matching_warm_card_and_primary_action_tokens():
    android = (ROOT / "android/app/src/main/res/layout/activity_payment_method.xml").read_text(encoding="utf-8")
    ios = IOS_PAYMENT_METHOD_VC.read_text(encoding="utf-8")
    for token in ("brand_background", "brand_primary_dark", "brand_surface", "brand_border", "brand_primary"):
        assert token in android
    for token in ("AppTheme.Colors.background", "AppTheme.Colors.secondaryBackground", "AppTheme.Colors.primary", "CornerRadius.planCard"):
        assert token in ios
    assert 'app:cornerRadius="12dp"' in android
    assert "heightAnchor.constraint(equalToConstant: 56)" in ios


def test_remaining_android_entry_pages_use_shared_brand_background_tokens():
    for relative_path in (
        "android/app/src/main/res/layout/activity_profile.xml",
        "android/app/src/main/res/layout/fragment_plan_list.xml",
        "android/app/src/main/res/layout/fragment_profile.xml",
    ):
        layout = (ROOT / relative_path).read_text(encoding="utf-8")
        assert "xui_config_color_background" not in layout
    plan_list = (ROOT / "android/app/src/main/res/layout/fragment_plan_list.xml").read_text(encoding="utf-8")
    assert "xui_config_color_primary" not in plan_list
    assert plan_list.count("@color/brand_primary") >= 4


def test_auth_and_profile_forms_use_matching_labels_and_validation_boundaries():
    android_register = ANDROID_REGISTER.read_text(encoding="utf-8")
    android_edit = ANDROID_EDIT_PROFILE.read_text(encoding="utf-8")
    ios_register = IOS_REGISTER.read_text(encoding="utf-8")
    ios_edit = IOS_EDIT_PROFILE.read_text(encoding="utf-8")

    for text in ("邮箱", "昵称", "确认密码", "性别", "年龄", "身高", "当前体重", "注册"):
        assert text in android_register
        assert text in ios_register
    for text in ("编辑个人信息", "昵称", "性别", "年龄", "身高", "当前体重", "目标体重", "保存"):
        assert text in android_edit
        assert text in ios_edit

    # Android 与 iOS 都只能提交后端允许的注册边界，且性别选项一致。
    assert 'age >= 13 && age <= 120' in ios_register
    assert 'height >= 100 && height <= 250' in ios_register
    assert 'weight >= 30 && weight <= 300' in ios_register
    assert 'items = ["男", "女"]' in ios_register
    assert 'items: ["男", "女"]' in ios_edit
    assert '"Other"' not in ios_edit


def test_plan_list_renders_expired_state_and_two_decimal_amount_on_both_platforms():
    android = ANDROID_PLAN_ADAPTER.read_text(encoding="utf-8")
    ios = IOS_PLANS.read_text(encoding="utf-8")
    assert '"expired" -> "已过期"' in android
    assert 'String.format(Locale.getDefault(), "%.2f", plan.betAmount)' in android
    assert 'case .expired:' in ios
    assert 'String(format: "%.2f", plan.betAmount)' in ios
    assert '赌金: ¥${String.format(Locale.getDefault(), "%.2f", plan.betAmount)}' in android
    assert 'betAmountLabel.text = "赌金: ¥\\(String(format: "%.2f", plan.betAmount))"' in ios
    assert 'goalText = if (plan.creatorInitialWeight != null && plan.creatorTargetWeight != null)' in android
    assert 'goalLabel.text = "目标: \\(String(format: "%.1f", plan.creatorInitialWeight))kg → \\(String(format: "%.1f", plan.creatorTargetWeight))kg"' in ios
    assert 'emptyStateLabel.text = "还没有计划\\n创建一个轻量挑战，和朋友一起坚持"' in ios


def test_plan_list_visual_tokens_match_the_shared_warm_lifestyle_direction():
    android_layout = (ROOT / "android/app/src/main/res/layout/activity_plan_list.xml").read_text(encoding="utf-8")
    android_card = (ROOT / "android/app/src/main/res/layout/item_betting_plan.xml").read_text(encoding="utf-8")
    ios = IOS_PLANS.read_text(encoding="utf-8")

    for token in ("@color/brand_background", "@color/brand_text", "@color/brand_surface_alt", "@color/brand_border"):
        assert token in android_layout
    assert '@color/brand_surface' in android_card
    assert 'app:cardCornerRadius="20dp"' in android_card
    assert 'AppTheme.Colors.background' in ios
    assert 'AppTheme.CornerRadius.planCard' in ios
    assert 'AppTheme.Colors.separator.withAlphaComponent(0.45)' in ios
    assert '还没有计划\\n创建一个轻量挑战，和朋友一起坚持' in ios


def test_transaction_history_uses_matching_chinese_labels_and_safe_amount_format():
    android = ANDROID_TRANSACTION_ADAPTER.read_text(encoding="utf-8")
    ios = IOS_BALANCE.read_text(encoding="utf-8")
    for text in ("充值", "冻结", "解冻", "转账", "提现", "退款", "处理中", "已完成", "失败"):
        assert text in android
        assert text in ios
    assert 'abs(transaction.amount)' in android
    assert 'String(format: "%.2f", abs(transaction.amount))' in ios
    assert 'SimpleDateFormat("MM-dd HH:mm"' in android
    assert 'formatter.dateFormat = "MM-dd HH:mm"' in ios


def test_ios_balance_buttons_open_code_based_payment_pages():
    ios = IOS_BALANCE.read_text(encoding="utf-8")
    assert 'let chargeVC = ChargeViewController()' in ios
    assert 'let withdrawVC = WithdrawViewController()' in ios
    assert 'UIStoryboard(name: "Main"' not in ios


def test_balance_page_uses_the_shared_card_and_payment_action_hierarchy():
    android = (ROOT / "android/app/src/main/res/layout/activity_balance.xml").read_text(encoding="utf-8")
    ios = IOS_BALANCE.read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'app:cardCornerRadius="20dp"' in android
    assert 'app:strokeColor="@color/brand_border"' in android
    assert 'android:id="@+id/btnCharge"' in android
    assert 'android:backgroundTint="@color/brand_primary"' in android
    assert 'android:id="@+id/btnWithdraw"' in android
    assert 'withdrawButton.backgroundColor = AppTheme.Colors.secondaryBackground' in ios
    assert 'withdrawButton.layer.borderColor = AppTheme.Colors.primary.cgColor' in ios


def test_check_in_page_uses_matching_brand_background_and_primary_action():
    android = (ROOT / "android/app/src/main/res/layout/activity_check_in.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/CheckIn/CheckInViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:background="@color/brand_primary_dark"' in android
    assert 'android:id="@+id/btnSubmit"' in android
    assert 'android:backgroundTint="@color/brand_accent"' in android
    assert 'button.backgroundColor = AppTheme.Colors.accent' in ios
    assert 'button.layer.cornerRadius = AppTheme.CornerRadius.large' in ios
    assert 'button.layer.borderColor = AppTheme.Colors.primary.cgColor' in ios
    assert 'selectPhotoButton.heightAnchor.constraint(equalToConstant: 48)' in ios


def test_plan_detail_uses_matching_surface_and_action_semantics():
    android = (ROOT / "android/app/src/main/res/layout/activity_plan_detail.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Plans/PlanDetailViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:background="@color/brand_primary_dark"' in android
    assert 'app:cardBackgroundColor="@color/brand_surface"' in android
    assert 'app:strokeColor="@color/brand_border"' in android
    assert 'betAmountLabel.textColor = AppTheme.Colors.primaryDark' in ios
    assert 'checkInButton.backgroundColor = AppTheme.Colors.accent' in ios
    assert 'giveUpButton.backgroundColor = AppTheme.Colors.error' in ios


def test_check_in_history_uses_matching_card_and_empty_state_language():
    android = (ROOT / "android/app/src/main/res/layout/activity_check_in_history.xml").read_text(encoding="utf-8")
    android_item = (ROOT / "android/app/src/main/res/layout/item_check_in_history.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/CheckIn/CheckInHistoryViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert '还没有打卡记录&#10;完成一次打卡后会显示在这里' in android
    assert 'app:cardBackgroundColor="@color/brand_surface"' in android_item
    assert 'app:cardCornerRadius="20dp"' in android_item
    assert '还没有打卡记录\\n完成一次打卡后会显示在这里' in ios
    assert 'AppTheme.CornerRadius.planCard' in ios
    assert 'tableView.separatorStyle = .none' in ios


def test_payment_forms_use_matching_input_and_primary_action_tokens():
    android_charge = (ROOT / "android/app/src/main/res/layout/activity_charge.xml").read_text(encoding="utf-8")
    android_withdraw = (ROOT / "android/app/src/main/res/layout/activity_withdraw.xml").read_text(encoding="utf-8")
    ios_charge = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewController.swift").read_text(encoding="utf-8")
    ios_withdraw = (ROOT / "ios/WeightLossBetting/UI/Payment/WithdrawViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android_charge
    assert 'android:backgroundTint="@color/brand_primary"' in android_charge
    assert 'android:backgroundTint="@color/brand_primary"' in android_withdraw
    assert 'app:cornerRadius="12dp"' in android_charge
    assert 'textField.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios_charge
    assert 'textField.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios_withdraw
    assert 'button.backgroundColor = AppTheme.Colors.primary' in ios_withdraw


def test_auth_pages_use_matching_brand_background_and_action_tokens():
    android_login = (ROOT / "android/app/src/main/res/layout/activity_login.xml").read_text(encoding="utf-8")
    android_register = (ROOT / "android/app/src/main/res/layout/activity_register.xml").read_text(encoding="utf-8")
    ios_login = (ROOT / "ios/WeightLossBetting/UI/Auth/LoginViewController.swift").read_text(encoding="utf-8")
    ios_register = (ROOT / "ios/WeightLossBetting/UI/Auth/RegisterViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android_login
    assert 'android:background="@color/brand_background"' in android_register
    assert 'android:backgroundTint="@color/brand_primary"' in android_login
    assert 'android:backgroundTint="@color/brand_primary"' in android_register
    assert 'button.setTitleColor(AppTheme.Colors.primary, for: .normal)' in ios_login
    assert 'button.layer.borderColor = AppTheme.Colors.primary.cgColor' in ios_login
    assert 'field.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios_register


def test_create_plan_uses_matching_brand_form_and_primary_action_tokens():
    android = (ROOT / "android/app/src/main/res/layout/activity_create_plan.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Plans/CreatePlanViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:background="@color/brand_primary_dark"' in android
    assert 'com.google.android.material.button.MaterialButton' in android
    assert 'android:backgroundTint="@color/brand_primary"' in android
    assert 'app:rb_backgroundColor' not in android
    assert 'textField.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios
    assert 'descriptionTextView.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios
    assert 'createButton.heightAnchor.constraint(equalToConstant: 56)' in ios


def test_coach_page_uses_matching_surface_cards_and_brand_background():
    android = (ROOT / "android/app/src/main/res/layout/fragment_coach.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Main/CoachViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'app:cardBackgroundColor="@color/brand_surface"' in android
    assert 'app:cardElevation="2dp"' in android
    assert 'card.layer.borderWidth = 1' in ios
    assert 'card.applyShadow(style: AppTheme.Shadow.small())' in ios


def test_comments_page_uses_matching_cards_and_composer_actions():
    android = (ROOT / "android/app/src/main/res/layout/activity_comments.xml").read_text(encoding="utf-8")
    android_item = (ROOT / "android/app/src/main/res/layout/item_comment.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Social/CommentsViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:backgroundTint="@color/brand_primary"' in android
    assert 'app:cardBackgroundColor="@color/brand_surface"' in android_item
    assert 'app:cardCornerRadius="20dp"' in android_item
    assert 'table.separatorStyle = .none' in ios
    assert 'sendButton.backgroundColor = AppTheme.Colors.primary' in ios
    assert 'contentView.layer.cornerRadius = AppTheme.CornerRadius.planCard' in ios


def test_progress_page_uses_matching_metric_card_surfaces():
    android = (ROOT / "android/app/src/main/res/layout/activity_progress.xml").read_text(encoding="utf-8")
    drawable = (ROOT / "android/app/src/main/res/drawable/bg_metric_card.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/CheckIn/ProgressViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:background="@drawable/bg_metric_card"' in android
    assert '@color/brand_surface' in drawable
    assert 'android:radius="16dp"' in drawable
    assert 'view.layer.borderWidth = 1' in ios
    assert 'AppTheme.Colors.secondaryBackground' in ios


def test_leaderboard_uses_matching_tabs_and_rank_cards():
    android = (ROOT / "android/app/src/main/res/layout/activity_leaderboard.xml").read_text(encoding="utf-8")
    android_item = (ROOT / "android/app/src/main/res/layout/item_leaderboard.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Social/LeaderboardViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'app:tabIndicatorColor="@color/brand_primary"' in android
    assert 'app:tabSelectedTextColor="@color/brand_primary"' in android
    assert 'app:cardBackgroundColor="@color/brand_surface"' in android_item
    assert 'app:cardCornerRadius="20dp"' in android_item
    assert 'segmentedControl.selectedSegmentTintColor = AppTheme.Colors.primary' in ios
    assert 'table.separatorStyle = .none' in ios
    assert 'contentView.layer.cornerRadius = AppTheme.CornerRadius.planCard' in ios


def test_badges_page_uses_matching_surface_cards_and_brand_navigation():
    android = (ROOT / "android/app/src/main/res/layout/activity_badges.xml").read_text(encoding="utf-8")
    android_item = (ROOT / "android/app/src/main/res/layout/item_badge.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Social/BadgesViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:background="@color/brand_primary_dark"' in android
    assert 'app:cardBackgroundColor="@color/brand_surface"' in android_item
    assert 'app:cardCornerRadius="20dp"' in android_item
    assert 'view.layer.cornerRadius = AppTheme.CornerRadius.planCard' in ios
    assert 'view.layer.borderWidth = 1' in ios


def test_main_navigation_uses_matching_four_item_brand_tinting():
    android = (ROOT / "android/app/src/main/res/layout/activity_main.xml").read_text(encoding="utf-8")
    android_tint = (ROOT / "android/app/src/main/res/color/bottom_nav_item_tint.xml").read_text(encoding="utf-8")
    android_menu = (ROOT / "android/app/src/main/res/menu/bottom_navigation_menu.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Main/MainTabBarController.swift").read_text(encoding="utf-8")

    for item in ("navigation_home", "navigation_coach", "navigation_plans", "navigation_profile"):
        assert item in android_menu
    assert 'app:itemIconTint="@color/bottom_nav_item_tint"' in android
    assert 'app:itemTextColor="@color/bottom_nav_item_tint"' in android
    assert 'android:state_checked="true"' in android_tint
    assert 'tabBar.backgroundColor = AppTheme.Colors.secondaryBackground' in ios


def test_settlement_page_uses_matching_selection_and_action_tokens():
    android = (ROOT / "android/app/src/main/res/layout/activity_settlement.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Settlement/SettlementViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:background="@color/brand_primary_dark"' in android
    assert 'android:backgroundTint="@color/brand_primary"' in android
    assert 'segment.selectedSegmentTintColor = AppTheme.Colors.primary' in ios
    assert 'submitButton.heightAnchor.constraint(equalToConstant: 56)' in ios
    assert 'button.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios


def test_edit_profile_uses_matching_form_and_save_action_tokens():
    android = (ROOT / "android/app/src/main/res/layout/activity_edit_profile.xml").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Profile/EditProfileViewController.swift").read_text(encoding="utf-8")

    assert 'android:background="@color/brand_background"' in android
    assert 'android:backgroundTint="@color/brand_primary"' in android
    assert 'app:cornerRadius="12dp"' in android
    assert 'field.layer.cornerRadius = AppTheme.CornerRadius.medium' in ios
    assert 'genderSegmentedControl.selectedSegmentTintColor = AppTheme.Colors.primary' in ios
    assert 'saveButton.heightAnchor.constraint(equalToConstant: 56)' in ios


def test_login_google_separator_and_register_copy_match_between_platforms():
    android = ANDROID_LOGIN_LAYOUT.read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Auth/LoginViewController.swift").read_text(encoding="utf-8")
    assert 'android:id="@+id/tvOr"' in android
    assert 'android:text="或者"' in android
    assert 'label.text = "或者"' in ios
    assert 'android:text="还没有账号？立即注册"' in android
    assert 'button.setTitle("还没有账号？立即注册"' in ios


def test_profile_exposes_the_same_settings_entry_and_hides_legacy_payment_entry():
    android_layout = ANDROID_PROFILE_LAYOUT.read_text(encoding="utf-8")
    android_fragment = ANDROID_PROFILE_FRAGMENT.read_text(encoding="utf-8")
    ios = IOS_PROFILE.read_text(encoding="utf-8")

    assert 'android:id="@+id/btnNotificationSettings"' in android_layout
    assert 'android:text="通知设置"' in android_layout
    assert "binding.btnNotificationSettings.setOnClickListener" in android_fragment
    assert "ACTION_APP_NOTIFICATION_SETTINGS" in android_fragment
    assert 'button.setTitle("通知设置"' in ios


def test_profile_visual_hierarchy_uses_matching_card_and_action_semantics():
    android_layout = ANDROID_PROFILE_LAYOUT.read_text(encoding="utf-8")
    android_card = (ROOT / "android/app/src/main/res/drawable/bg_card.xml").read_text(encoding="utf-8")
    ios = IOS_PROFILE.read_text(encoding="utf-8")

    assert 'android:background="@drawable/bg_card"' in android_layout
    assert 'android:layout_height="52dp"' in android_layout
    assert 'app:cornerRadius="12dp"' in android_layout
    assert 'android:backgroundTint="@color/brand_primary"' in android_layout
    assert '@color/brand_surface' in android_card
    assert 'android:radius="20dp"' in android_card
    assert 'button.backgroundColor = AppTheme.Colors.primary' in ios
    assert 'button.layer.cornerRadius = 12' in ios

    # 绑定银行卡只保留在独立的 Stripe SetupIntent 页面，个人页不能再暴露旧入口。
    assert 'android:id="@+id/btnPaymentMethod"' not in android_layout
    assert "button.isHidden = true" in ios


def test_active_plan_detail_exposes_matching_progress_history_and_comments_actions():
    android = ANDROID_PLAN_DETAIL.read_text(encoding="utf-8")
    ios = IOS_PLAN_DETAIL.read_text(encoding="utf-8")

    for text in ("btnCheckIn", "btnProgress", "btnCheckInHistory", "btnComments", 'plan.status == "active"'):
        assert text in android
    for text in ("progressButton", "checkInHistoryButton", "commentsButton", "inviteButton", "ProgressViewController", "CheckInHistoryViewController", "CommentsViewController", "InviteViewController"):
        assert text in ios
    for text in ("查看进度", "查看打卡历史", "查看评论"):
        assert text in ios
    assert "progressButton.isHidden = false" in ios
    assert "checkInHistoryButton.isHidden = false" in ios
    assert "commentsButton.isHidden = false" in ios
    assert "showCancelOnly(showInvite: plan.participantId == nil)" in ios
    assert 'inviteButton.setTitle("邀请好友"' in ios


def test_settlement_dispute_entry_matches_on_android_and_ios():
    android_activity = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/settlement/SettlementActivity.kt").read_text(encoding="utf-8")
    android_api = (ROOT / "android/app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt").read_text(encoding="utf-8")
    ios_controller = (ROOT / "ios/WeightLossBetting/UI/Settlement/SettlementViewController.swift").read_text(encoding="utf-8")
    ios_api = (ROOT / "ios/WeightLossBetting/Data/Network/APIService.swift").read_text(encoding="utf-8")

    for text in ("反馈结算问题", "争议状态", "至少10个字", "submitDispute"):
        assert text in android_activity
    for text in ("反馈结算问题", "争议状态", "至少填写10个字", "submitDispute"):
        assert text in ios_controller
    assert "submitDispute" in android_api
    assert "submitDispute" in ios_api


def test_admin_dispute_console_exposes_full_review_state_flow():
    admin = (ROOT / "backend/admin/index.html").read_text(encoding="utf-8")
    assert "接手审核" in admin
    assert "under_review" in admin
    assert "x.description" in admin
    assert "x.admin_notes" in admin
    assert "updateDispute" in admin


def test_settlement_pages_refresh_dispute_status_after_returning_to_foreground():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/settlement/SettlementActivity.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Settlement/SettlementViewController.swift").read_text(encoding="utf-8")
    assert "override fun onResume()" in android
    assert "hasLeftScreen" in android
    assert "viewWillAppear" in ios
    assert "hasAppeared" in ios
    assert "loadSettlementStatus()" in ios
