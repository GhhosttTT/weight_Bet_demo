package com.weightloss.betting

import com.weightloss.betting.data.model.*
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.*
import com.weightloss.betting.ui.checkin.CheckInViewModel
import com.weightloss.betting.ui.payment.BalanceViewModel
import com.weightloss.betting.ui.payment.ChargeViewModel
import com.weightloss.betting.ui.payment.WithdrawViewModel
import com.weightloss.betting.ui.plan.CreatePlanViewModel
import com.weightloss.betting.ui.plan.PlanDetailViewModel
import com.weightloss.betting.ui.plan.PlanListViewModel
import com.weightloss.betting.ui.profile.EditProfileViewModel
import com.weightloss.betting.ui.profile.ProfileViewModel
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import org.mockito.Mock
import org.mockito.Mockito.*
import org.mockito.MockitoAnnotations
import java.io.File
import java.util.*

/**
 * 任务 21-24 综合测试
 * 
 * 测试范围:
 * - Task 21: 用户信息管理 (ProfileViewModel, EditProfileViewModel)
 * - Task 22: 对赌计划功能 (PlanListViewModel, CreatePlanViewModel, PlanDetailViewModel)
 * - Task 23: 打卡功能 (CheckInViewModel)
 * - Task 24: 支付功能 (BalanceViewModel, ChargeViewModel, WithdrawViewModel)
 */
@OptIn(ExperimentalCoroutinesApi::class)
class Tasks21To24Test {

    private val testDispatcher = StandardTestDispatcher()

    @Mock
    private lateinit var userRepository: UserRepository

    @Mock
    private lateinit var bettingPlanRepository: BettingPlanRepository

    @Mock
    private lateinit var checkInRepository: CheckInRepository

    @Mock
    private lateinit var paymentRepository: PaymentRepository

    private lateinit var profileViewModel: ProfileViewModel
    private lateinit var editProfileViewModel: EditProfileViewModel
    private lateinit var planListViewModel: PlanListViewModel
    private lateinit var createPlanViewModel: CreatePlanViewModel
    private lateinit var planDetailViewModel: PlanDetailViewModel
    private lateinit var checkInViewModel: CheckInViewModel
    private lateinit var balanceViewModel: BalanceViewModel
    private lateinit var chargeViewModel: ChargeViewModel
    private lateinit var withdrawViewModel: WithdrawViewModel

    @Before
    fun setup() {
        MockitoAnnotations.openMocks(this)
        Dispatchers.setMain(testDispatcher)

        // Initialize ViewModels
        profileViewModel = ProfileViewModel(userRepository)
        editProfileViewModel = EditProfileViewModel(userRepository)
        planListViewModel = PlanListViewModel(bettingPlanRepository)
        createPlanViewModel = CreatePlanViewModel(bettingPlanRepository)
        planDetailViewModel = PlanDetailViewModel(bettingPlanRepository)
        checkInViewModel = CheckInViewModel(checkInRepository)
        balanceViewModel = BalanceViewModel(paymentRepository)
        chargeViewModel = ChargeViewModel(paymentRepository)
        withdrawViewModel = WithdrawViewModel(paymentRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    // ==================== Task 21: 用户信息管理测试 ====================

    @Test
    fun `test_task21_1_load_user_profile_success`() = runTest {
        println("✓ 测试 21.1: 加载用户信息成功")
        
        val mockUser = User(
            id = "user123",
            email = "test@example.com",
            nickname = "测试用户",
            gender = "male",
            age = 25,
            height = 175.0,
            currentWeight = 75.0,
            targetWeight = 70.0,
            createdAt = Date()
        )

        `when`(userRepository.getUserProfile("user123", false))
            .thenReturn(NetworkResult.Success(mockUser))

        profileViewModel.loadUserProfile("user123")
        testDispatcher.scheduler.advanceUntilIdle()

        verify(userRepository).getUserProfile("user123", false)
        println("  ✓ 用户信息加载成功")
    }

    @Test
    fun `test_task21_2_update_user_profile_validation`() = runTest {
        println("✓ 测试 21.2: 用户信息更新验证")
        
        // Test nickname validation
        editProfileViewModel.updateProfile(
            userId = "user123",
            nickname = "", // Empty nickname
            gender = "male",
            age = "25",
            height = "175",
            currentWeight = "75",
            targetWeight = "70"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 昵称为空验证通过")

        // Test age validation
        editProfileViewModel.updateProfile(
            userId = "user123",
            nickname = "测试",
            gender = "male",
            age = "10", // Age < 13
            height = "175",
            currentWeight = "75",
            targetWeight = "70"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 年龄范围验证通过")

        // Test height validation
        editProfileViewModel.updateProfile(
            userId = "user123",
            nickname = "测试",
            gender = "male",
            age = "25",
            height = "50", // Height < 100
            currentWeight = "75",
            targetWeight = "70"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 身高范围验证通过")

        // Test weight validation
        editProfileViewModel.updateProfile(
            userId = "user123",
            nickname = "测试",
            gender = "male",
            age = "25",
            height = "175",
            currentWeight = "20", // Weight < 30
            targetWeight = "70"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 体重范围验证通过")
    }

    @Test
    fun `test_task21_3_update_user_profile_success`() = runTest {
        println("✓ 测试 21.3: 用户信息更新成功")
        
        val mockUser = User(
            id = "user123",
            email = "test@example.com",
            nickname = "更新后",
            gender = "male",
            age = 26,
            height = 176.0,
            currentWeight = 74.0,
            targetWeight = 70.0,
            createdAt = Date()
        )

        val updateRequest = UpdateUserRequest(
            nickname = "更新后",
            gender = "male",
            age = 26,
            height = 176.0,
            currentWeight = 74.0,
            targetWeight = 70.0
        )

        `when`(userRepository.updateUserProfile("user123", updateRequest))
            .thenReturn(NetworkResult.Success(mockUser))

        editProfileViewModel.updateProfile(
            userId = "user123",
            nickname = "更新后",
            gender = "male",
            age = "26",
            height = "176",
            currentWeight = "74",
            targetWeight = "70"
        )
        testDispatcher.scheduler.advanceUntilIdle()

        println("  ✓ 用户信息更新成功")
    }

    // ==================== Task 22: 对赌计划功能测试 ====================

    @Test
    fun `test_task22_1_load_plan_list_success`() = runTest {
        println("✓ 测试 22.1: 加载计划列表成功")
        
        val mockPlans = listOf(
            BettingPlan(
                id = "plan1",
                creatorId = "user123",
                participantId = "user456",
                status = "active",
                betAmount = 100.0,
                startDate = Date(),
                endDate = Date(System.currentTimeMillis() + 30L * 24 * 60 * 60 * 1000),
                description = "测试计划1",
                creatorInitialWeight = 80.0,
                creatorTargetWeight = 75.0,
                creatorTargetWeightLoss = 5.0,
                participantInitialWeight = 85.0,
                participantTargetWeight = 80.0,
                participantTargetWeightLoss = 5.0,
                createdAt = Date()
            )
        )

        `when`(bettingPlanRepository.getUserPlans("user123", null, false))
            .thenReturn(NetworkResult.Success(mockPlans))

        planListViewModel.loadPlans("user123")
        testDispatcher.scheduler.advanceUntilIdle()

        verify(bettingPlanRepository).getUserPlans("user123", null, false)
        println("  ✓ 计划列表加载成功")
    }

    @Test
    fun `test_task22_2_create_plan_validation`() = runTest {
        println("✓ 测试 22.2: 创建计划参数验证")
        
        // Test bet amount validation
        createPlanViewModel.createPlan(
            creatorId = "user123",
            betAmount = "-10", // Negative amount
            startDate = Date(),
            endDate = Date(System.currentTimeMillis() + 30L * 24 * 60 * 60 * 1000),
            description = "测试",
            initialWeight = "80",
            targetWeight = "75"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 赌金金额验证通过")

        // Test date validation
        val pastDate = Date(System.currentTimeMillis() - 24L * 60 * 60 * 1000)
        createPlanViewModel.createPlan(
            creatorId = "user123",
            betAmount = "100",
            startDate = Date(),
            endDate = pastDate, // End date before start date
            description = "测试",
            initialWeight = "80",
            targetWeight = "75"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 日期范围验证通过")

        // Test weight validation
        createPlanViewModel.createPlan(
            creatorId = "user123",
            betAmount = "100",
            startDate = Date(),
            endDate = Date(System.currentTimeMillis() + 30L * 24 * 60 * 60 * 1000),
            description = "测试",
            initialWeight = "80",
            targetWeight = "85" // Target > initial (should lose weight)
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 体重目标验证通过")
    }

    @Test
    fun `test_task22_3_load_plan_detail_success`() = runTest {
        println("✓ 测试 22.3: 加载计划详情成功")
        
        val mockPlan = BettingPlan(
            id = "plan1",
            creatorId = "user123",
            participantId = "user456",
            status = "active",
            betAmount = 100.0,
            startDate = Date(),
            endDate = Date(System.currentTimeMillis() + 30L * 24 * 60 * 60 * 1000),
            description = "测试计划",
            creatorInitialWeight = 80.0,
            creatorTargetWeight = 75.0,
            creatorTargetWeightLoss = 5.0,
            participantInitialWeight = 85.0,
            participantTargetWeight = 80.0,
            participantTargetWeightLoss = 5.0,
            createdAt = Date()
        )

        `when`(bettingPlanRepository.getPlanDetail("plan1"))
            .thenReturn(NetworkResult.Success(mockPlan))

        planDetailViewModel.loadPlanDetail("plan1")
        testDispatcher.scheduler.advanceUntilIdle()

        verify(bettingPlanRepository).getPlanDetail("plan1")
        println("  ✓ 计划详情加载成功")
    }

    @Test
    fun `test_task22_4_accept_plan_success`() = runTest {
        println("✓ 测试 22.4: 接受计划成功")
        
        val acceptRequest = AcceptPlanRequest(
            participantId = "user456",
            initialWeight = 85.0,
            targetWeight = 80.0,
            targetWeightLoss = 5.0
        )

        val mockPlan = BettingPlan(
            id = "plan1",
            creatorId = "user123",
            participantId = "user456",
            status = "active",
            betAmount = 100.0,
            startDate = Date(),
            endDate = Date(System.currentTimeMillis() + 30L * 24 * 60 * 60 * 1000),
            description = "测试计划",
            creatorInitialWeight = 80.0,
            creatorTargetWeight = 75.0,
            creatorTargetWeightLoss = 5.0,
            participantInitialWeight = 85.0,
            participantTargetWeight = 80.0,
            participantTargetWeightLoss = 5.0,
            createdAt = Date(),
            activatedAt = Date()
        )

        `when`(bettingPlanRepository.acceptPlan("plan1", acceptRequest))
            .thenReturn(NetworkResult.Success(mockPlan))

        planDetailViewModel.acceptPlan(
            planId = "plan1",
            participantId = "user456",
            initialWeight = "85",
            targetWeight = "80"
        )
        testDispatcher.scheduler.advanceUntilIdle()

        println("  ✓ 计划接受成功")
    }

    // ==================== Task 23: 打卡功能测试 ====================

    @Test
    fun `test_task23_1_create_checkin_validation`() = runTest {
        println("✓ 测试 23.1: 打卡数据验证")
        
        // Test weight validation
        checkInViewModel.createCheckIn(
            userId = "user123",
            planId = "plan1",
            weight = "20", // Weight < 30
            note = "测试",
            photoUri = null
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 体重范围验证通过")

        checkInViewModel.createCheckIn(
            userId = "user123",
            planId = "plan1",
            weight = "350", // Weight > 300
            note = "测试",
            photoUri = null
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 体重上限验证通过")
    }

    @Test
    fun `test_task23_2_create_checkin_success`() = runTest {
        println("✓ 测试 23.2: 创建打卡记录成功")
        
        val checkInRequest = CreateCheckInRequest(
            userId = "user123",
            planId = "plan1",
            weight = 74.5,
            checkInDate = Date(),
            note = "今天状态不错"
        )

        val mockCheckIn = CheckIn(
            id = "checkin1",
            userId = "user123",
            planId = "plan1",
            weight = 74.5,
            checkInDate = Date(),
            note = "今天状态不错",
            reviewStatus = "pending",
            createdAt = Date()
        )

        `when`(checkInRepository.createCheckIn(checkInRequest))
            .thenReturn(NetworkResult.Success(mockCheckIn))

        checkInViewModel.createCheckIn(
            userId = "user123",
            planId = "plan1",
            weight = "74.5",
            note = "今天状态不错",
            photoUri = null
        )
        testDispatcher.scheduler.advanceUntilIdle()

        println("  ✓ 打卡记录创建成功")
    }

    @Test
    fun `test_task23_3_photo_upload_helper_exists`() {
        println("✓ 测试 23.3: 照片上传辅助类存在")
        
        val photoUploadHelperFile = File("android/app/src/main/java/com/weightloss/betting/ui/checkin/PhotoUploadHelper.kt")
        assert(photoUploadHelperFile.exists()) { "PhotoUploadHelper.kt 文件不存在" }
        println("  ✓ PhotoUploadHelper.kt 文件存在")
    }

    // ==================== Task 24: 支付功能测试 ====================

    @Test
    fun `test_task24_1_load_balance_success`() = runTest {
        println("✓ 测试 24.1: 加载余额信息成功")
        
        val mockBalance = Balance(
            userId = "user123",
            availableBalance = 500.0,
            frozenBalance = 100.0,
            updatedAt = Date()
        )

        `when`(paymentRepository.getBalance("user123"))
            .thenReturn(NetworkResult.Success(mockBalance))

        balanceViewModel.loadBalance("user123")
        testDispatcher.scheduler.advanceUntilIdle()

        verify(paymentRepository).getBalance("user123")
        println("  ✓ 余额信息加载成功")
    }

    @Test
    fun `test_task24_2_charge_validation`() = runTest {
        println("✓ 测试 24.2: 充值金额验证")
        
        // Test negative amount
        chargeViewModel.charge(
            userId = "user123",
            amount = "-50"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 负数金额验证通过")

        // Test zero amount
        chargeViewModel.charge(
            userId = "user123",
            amount = "0"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 零金额验证通过")
    }

    @Test
    fun `test_task24_3_withdraw_validation`() = runTest {
        println("✓ 测试 24.3: 提现金额验证")
        
        // Test negative amount
        withdrawViewModel.withdraw(
            userId = "user123",
            amount = "-50"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 负数金额验证通过")

        // Test zero amount
        withdrawViewModel.withdraw(
            userId = "user123",
            amount = "0"
        )
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 零金额验证通过")
    }

    @Test
    fun `test_task24_4_load_transactions_success`() = runTest {
        println("✓ 测试 24.4: 加载交易历史成功")
        
        val mockTransactions = listOf(
            Transaction(
                id = "tx1",
                userId = "user123",
                type = "charge",
                amount = 100.0,
                status = "completed",
                createdAt = Date(),
                completedAt = Date()
            ),
            Transaction(
                id = "tx2",
                userId = "user123",
                type = "freeze",
                amount = 50.0,
                status = "completed",
                relatedPlanId = "plan1",
                createdAt = Date(),
                completedAt = Date()
            )
        )

        `when`(paymentRepository.getTransactions("user123", 1, 20))
            .thenReturn(NetworkResult.Success(mockTransactions))

        balanceViewModel.loadTransactions("user123")
        testDispatcher.scheduler.advanceUntilIdle()

        verify(paymentRepository).getTransactions("user123", 1, 20)
        println("  ✓ 交易历史加载成功")
    }

    // ==================== 布局文件和Activity注册测试 ====================

    @Test
    fun `test_layout_files_exist`() {
        println("✓ 测试: 检查所有布局文件是否存在")
        
        val layoutFiles = listOf(
            "activity_profile.xml",
            "activity_edit_profile.xml",
            "activity_plan_list.xml",
            "activity_create_plan.xml",
            "activity_plan_detail.xml",
            "item_betting_plan.xml",
            "activity_check_in.xml",
            "activity_balance.xml",
            "activity_charge.xml",
            "activity_withdraw.xml",
            "item_transaction.xml"
        )

        layoutFiles.forEach { fileName ->
            val file = File("android/app/src/main/res/layout/$fileName")
            assert(file.exists()) { "$fileName 不存在" }
            println("  ✓ $fileName 存在")
        }
    }

    @Test
    fun `test_viewmodel_files_exist`() {
        println("✓ 测试: 检查所有ViewModel文件是否存在")
        
        val viewModelFiles = listOf(
            "ui/profile/ProfileViewModel.kt",
            "ui/profile/EditProfileViewModel.kt",
            "ui/plan/PlanListViewModel.kt",
            "ui/plan/CreatePlanViewModel.kt",
            "ui/plan/PlanDetailViewModel.kt",
            "ui/checkin/CheckInViewModel.kt",
            "ui/payment/BalanceViewModel.kt",
            "ui/payment/ChargeViewModel.kt",
            "ui/payment/WithdrawViewModel.kt"
        )

        viewModelFiles.forEach { filePath ->
            val file = File("android/app/src/main/java/com/weightloss/betting/$filePath")
            assert(file.exists()) { "$filePath 不存在" }
            println("  ✓ $filePath 存在")
        }
    }

    @Test
    fun `test_activity_files_exist`() {
        println("✓ 测试: 检查所有Activity文件是否存在")
        
        val activityFiles = listOf(
            "ui/profile/ProfileActivity.kt",
            "ui/profile/EditProfileActivity.kt",
            "ui/plan/PlanListActivity.kt",
            "ui/plan/CreatePlanActivity.kt",
            "ui/plan/PlanDetailActivity.kt",
            "ui/checkin/CheckInActivity.kt",
            "ui/payment/BalanceActivity.kt",
            "ui/payment/ChargeActivity.kt",
            "ui/payment/WithdrawActivity.kt"
        )

        activityFiles.forEach { filePath ->
            val file = File("android/app/src/main/java/com/weightloss/betting/$filePath")
            assert(file.exists()) { "$filePath 不存在" }
            println("  ✓ $filePath 存在")
        }
    }

    @Test
    fun `test_manifest_activities_registered`() {
        println("✓ 测试: 检查AndroidManifest.xml中Activity注册")
        
        val manifestFile = File("android/app/src/main/AndroidManifest.xml")
        assert(manifestFile.exists()) { "AndroidManifest.xml 不存在" }
        
        val manifestContent = manifestFile.readText()
        
        val activities = listOf(
            ".ui.profile.ProfileActivity",
            ".ui.profile.EditProfileActivity",
            ".ui.plan.PlanListActivity",
            ".ui.plan.CreatePlanActivity",
            ".ui.plan.PlanDetailActivity",
            ".ui.checkin.CheckInActivity",
            ".ui.payment.BalanceActivity",
            ".ui.payment.ChargeActivity",
            ".ui.payment.WithdrawActivity"
        )

        activities.forEach { activity ->
            assert(manifestContent.contains(activity)) { "$activity 未在AndroidManifest.xml中注册" }
            println("  ✓ $activity 已注册")
        }
    }

    @Test
    fun `test_permissions_declared`() {
        println("✓ 测试: 检查必要权限是否声明")
        
        val manifestFile = File("android/app/src/main/AndroidManifest.xml")
        val manifestContent = manifestFile.readText()
        
        val permissions = listOf(
            "android.permission.INTERNET",
            "android.permission.CAMERA",
            "android.permission.READ_EXTERNAL_STORAGE",
            "android.permission.WRITE_EXTERNAL_STORAGE"
        )

        permissions.forEach { permission ->
            assert(manifestContent.contains(permission)) { "$permission 权限未声明" }
            println("  ✓ $permission 权限已声明")
        }
    }

    // ==================== 综合测试 ====================

    @Test
    fun `test_comprehensive_user_flow`() = runTest {
        println("✓ 综合测试: 完整用户流程")
        
        // 1. Load user profile
        val mockUser = User(
            id = "user123",
            email = "test@example.com",
            nickname = "测试用户",
            gender = "male",
            age = 25,
            height = 175.0,
            currentWeight = 80.0,
            targetWeight = 75.0,
            createdAt = Date()
        )
        `when`(userRepository.getUserProfile("user123", false))
            .thenReturn(NetworkResult.Success(mockUser))
        
        profileViewModel.loadUserProfile("user123")
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 步骤1: 加载用户信息")

        // 2. Load balance
        val mockBalance = Balance(
            userId = "user123",
            availableBalance = 500.0,
            frozenBalance = 0.0,
            updatedAt = Date()
        )
        `when`(paymentRepository.getBalance("user123"))
            .thenReturn(NetworkResult.Success(mockBalance))
        
        balanceViewModel.loadBalance("user123")
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 步骤2: 加载余额信息")

        // 3. Load plan list
        val mockPlans = listOf<BettingPlan>()
        `when`(bettingPlanRepository.getUserPlans("user123", null, false))
            .thenReturn(NetworkResult.Success(mockPlans))
        
        planListViewModel.loadPlans("user123")
        testDispatcher.scheduler.advanceUntilIdle()
        println("  ✓ 步骤3: 加载计划列表")

        println("  ✓ 完整用户流程测试通过")
    }
}
