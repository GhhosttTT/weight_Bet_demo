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


def test_notification_permission_is_requested_once_on_android_like_ios_login_flow():
    android = ANDROID_MAIN.read_text(encoding="utf-8")
    helper = ANDROID_NOTIFICATION_HELPER.read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Auth/LoginViewController.swift").read_text(encoding="utf-8")

    assert "requestNotificationPermissionIfNeeded()" in android
    assert "PREF_NOTIFICATION_PERMISSION_REQUESTED" in android
    assert "hasNotificationPermission" in android
    assert "requestNotificationPermission" in helper
    assert "requestNotificationPermissionsIfNeeded" in ios


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
    assert "val nonce: String? = null" in models
    assert "googleLogin(idToken: String, nonce: String? = null)" in repository


def test_payment_failure_resets_idempotency_key_on_both_mobile_platforms():
    android = (ROOT / "android/app/src/main/java/com/weightloss/betting/ui/payment/ChargeViewModel.kt").read_text(encoding="utf-8")
    ios = (ROOT / "ios/WeightLossBetting/UI/Payment/ChargeViewModel.swift").read_text(encoding="utf-8")

    android_failure = android.split("fun paymentFailed", 1)[1].split("}", 1)[0]
    ios_failure = ios.split("func paymentFailed", 1)[1].split("}", 1)[0]
    assert "chargeIdempotencyKey = null" in android_failure
    assert "chargeIdempotencyKey = nil" in ios_failure


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
    assert 'emptyStateLabel.text = "暂无计划"' in ios


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
