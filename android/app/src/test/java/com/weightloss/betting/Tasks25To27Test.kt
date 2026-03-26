package com.weightloss.betting

import org.junit.Test
import org.junit.Assert.*
import java.io.File

/**
 * 任务 25-27 测试类
 * 测试 Android 通知功能、社交功能和 UI/UX 优化
 */
class Tasks25To27Test {

    private val projectRoot = System.getProperty("user.dir")
    private val androidRoot = if (File(projectRoot, "android").exists()) {
        File(projectRoot, "android")
    } else {
        File(projectRoot)
    }

    // ==================== 任务 25: 通知功能测试 ====================

    @Test
    fun test_25_1_fcm_service_exists() {
        val fcmService = File(androidRoot, "app/src/main/java/com/weightloss/betting/service/FCMService.kt")
        assertTrue("FCMService.kt 应该存在", fcmService.exists())
        
        val content = fcmService.readText()
        assertTrue("FCMService 应该继承 FirebaseMessagingService", 
            content.contains("FirebaseMessagingService"))
        assertTrue("FCMService 应该实现 onMessageReceived", 
            content.contains("onMessageReceived"))
        assertTrue("FCMService 应该实现 onNewToken", 
            content.contains("onNewToken"))
    }

    @Test
    fun test_25_1_notification_repository_exists() {
        val repo = File(androidRoot, "app/src/main/java/com/weightloss/betting/data/repository/NotificationRepository.kt")
        assertTrue("NotificationRepository.kt 应该存在", repo.exists())
        
        val content = repo.readText()
        assertTrue("NotificationRepository 应该有 registerDeviceToken 方法", 
            content.contains("registerDeviceToken"))
    }

    @Test
    fun test_25_2_notification_types_handled() {
        val fcmService = File(androidRoot, "app/src/main/java/com/weightloss/betting/service/FCMService.kt")
        val content = fcmService.readText()
        
        assertTrue("应该处理 invite 通知", content.contains("invite"))
        assertTrue("应该处理 plan_active 通知", content.contains("plan_active"))
        assertTrue("应该处理 settlement 通知", content.contains("settlement"))
        assertTrue("应该处理 check_in_reminder 通知", content.contains("check_in_reminder"))
    }

    @Test
    fun test_25_3_notification_permission_helper_exists() {
        val helper = File(androidRoot, "app/src/main/java/com/weightloss/betting/util/NotificationPermissionHelper.kt")
        assertTrue("NotificationPermissionHelper.kt 应该存在", helper.exists())
        
        val content = helper.readText()
        assertTrue("应该有 hasNotificationPermission 方法", 
            content.contains("hasNotificationPermission"))
        assertTrue("应该有 requestNotificationPermission 方法", 
            content.contains("requestNotificationPermission"))
    }

    @Test
    fun test_25_fcm_dependencies_in_gradle() {
        val buildGradle = File(androidRoot, "app/build.gradle")
        assertTrue("build.gradle 应该存在", buildGradle.exists())
        
        val content = buildGradle.readText()
        assertTrue("应该包含 Firebase BOM 依赖", 
            content.contains("firebase-bom"))
        assertTrue("应该包含 Firebase Messaging 依赖", 
            content.contains("firebase-messaging"))
        assertTrue("应该包含 google-services 插件", 
            content.contains("com.google.gms.google-services"))
    }

    @Test
    fun test_25_fcm_service_registered_in_manifest() {
        val manifest = File(androidRoot, "app/src/main/AndroidManifest.xml")
        assertTrue("AndroidManifest.xml 应该存在", manifest.exists())
        
        val content = manifest.readText()
        assertTrue("应该注册 FCMService", content.contains("FCMService"))
        assertTrue("应该有 MESSAGING_EVENT action", 
            content.contains("com.google.firebase.MESSAGING_EVENT"))
        assertTrue("应该有 POST_NOTIFICATIONS 权限", 
            content.contains("POST_NOTIFICATIONS"))
    }

    // ==================== 任务 26: 社交功能测试 ====================

    @Test
    fun test_26_1_leaderboard_activity_exists() {
        val activity = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardActivity.kt")
        assertTrue("LeaderboardActivity.kt 应该存在", activity.exists())
        
        val content = activity.readText()
        assertTrue("应该继承 AppCompatActivity", content.contains("AppCompatActivity"))
        assertTrue("应该使用 @AndroidEntryPoint", content.contains("@AndroidEntryPoint"))
    }

    @Test
    fun test_26_1_leaderboard_viewmodel_exists() {
        val viewModel = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardViewModel.kt")
        assertTrue("LeaderboardViewModel.kt 应该存在", viewModel.exists())
        
        val content = viewModel.readText()
        assertTrue("应该继承 ViewModel", content.contains("ViewModel"))
        assertTrue("应该有 loadLeaderboard 方法", content.contains("loadLeaderboard"))
    }

    @Test
    fun test_26_1_leaderboard_adapter_exists() {
        val adapter = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardAdapter.kt")
        assertTrue("LeaderboardAdapter.kt 应该存在", adapter.exists())
        
        val content = adapter.readText()
        assertTrue("应该继承 RecyclerView.Adapter", 
            content.contains("RecyclerView.Adapter"))
    }

    @Test
    fun test_26_1_leaderboard_layout_exists() {
        val layout = File(androidRoot, "app/src/main/res/layout/activity_leaderboard.xml")
        assertTrue("activity_leaderboard.xml 应该存在", layout.exists())
        
        val content = layout.readText()
        assertTrue("应该包含 TabLayout", content.contains("TabLayout"))
        assertTrue("应该包含 RecyclerView", content.contains("RecyclerView"))
        assertTrue("应该包含 SwipeRefreshLayout", content.contains("SwipeRefreshLayout"))
    }

    @Test
    fun test_26_1_leaderboard_item_layout_exists() {
        val layout = File(androidRoot, "app/src/main/res/layout/item_leaderboard.xml")
        assertTrue("item_leaderboard.xml 应该存在", layout.exists())
    }

    @Test
    fun test_26_2_comment_api_exists() {
        val apiService = File(androidRoot, "app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt")
        assertTrue("ApiService.kt 应该存在", apiService.exists())
        
        val content = apiService.readText()
        assertTrue("应该有 getComments API", content.contains("getComments"))
        assertTrue("应该有 postComment API", content.contains("postComment"))
    }

    @Test
    fun test_26_3_encourage_api_exists() {
        val apiService = File(androidRoot, "app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt")
        val content = apiService.readText()
        
        assertTrue("应该有 encourageUser API", content.contains("encourageUser"))
    }

    @Test
    fun test_26_4_badges_activity_exists() {
        val activity = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/social/BadgesActivity.kt")
        assertTrue("BadgesActivity.kt 应该存在", activity.exists())
        
        val content = activity.readText()
        assertTrue("应该继承 AppCompatActivity", content.contains("AppCompatActivity"))
    }

    @Test
    fun test_26_4_badges_viewmodel_exists() {
        val viewModel = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/social/BadgesViewModel.kt")
        assertTrue("BadgesViewModel.kt 应该存在", viewModel.exists())
        
        val content = viewModel.readText()
        assertTrue("应该有 loadBadges 方法", content.contains("loadBadges"))
    }

    @Test
    fun test_26_4_badges_layout_exists() {
        val layout = File(androidRoot, "app/src/main/res/layout/activity_badges.xml")
        assertTrue("activity_badges.xml 应该存在", layout.exists())
        
        val content = layout.readText()
        assertTrue("应该包含 RecyclerView", content.contains("RecyclerView"))
    }

    @Test
    fun test_26_social_activities_registered_in_manifest() {
        val manifest = File(androidRoot, "app/src/main/AndroidManifest.xml")
        val content = manifest.readText()
        
        assertTrue("应该注册 LeaderboardActivity", content.contains("LeaderboardActivity"))
        assertTrue("应该注册 BadgesActivity", content.contains("BadgesActivity"))
    }

    // ==================== 任务 27: UI/UX 优化测试 ====================

    @Test
    fun test_27_1_main_activity_updated() {
        val mainActivity = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/MainActivity.kt")
        assertTrue("MainActivity.kt 应该存在", mainActivity.exists())
        
        val content = mainActivity.readText()
        assertTrue("应该包含 BottomNavigationView", content.contains("BottomNavigationView"))
    }

    @Test
    fun test_27_1_main_activity_layout_exists() {
        val layout = File(androidRoot, "app/src/main/res/layout/activity_main.xml")
        assertTrue("activity_main.xml 应该存在", layout.exists())
        
        val content = layout.readText()
        assertTrue("应该包含 BottomNavigationView", content.contains("BottomNavigationView"))
        assertTrue("应该包含 FragmentContainerView 或 FrameLayout", 
            content.contains("FragmentContainerView") || content.contains("FrameLayout"))
    }

    @Test
    fun test_27_1_bottom_navigation_menu_exists() {
        val menu = File(androidRoot, "app/src/main/res/menu/bottom_navigation_menu.xml")
        assertTrue("bottom_navigation_menu.xml 应该存在", menu.exists())
        
        val content = menu.readText()
        assertTrue("应该有首页菜单项", content.contains("home") || content.contains("首页"))
        assertTrue("应该有计划菜单项", content.contains("plan") || content.contains("计划"))
        assertTrue("应该有打卡菜单项", content.contains("check") || content.contains("打卡"))
        assertTrue("应该有我的菜单项", content.contains("profile") || content.contains("我的"))
    }

    @Test
    fun test_27_1_home_fragment_exists() {
        val fragment = File(androidRoot, "app/src/main/java/com/weightloss/betting/ui/main/HomeFragment.kt")
        assertTrue("HomeFragment.kt 应该存在", fragment.exists())
        
        val content = fragment.readText()
        assertTrue("应该继承 Fragment", content.contains("Fragment"))
    }

    @Test
    fun test_27_1_home_fragment_layout_exists() {
        val layout = File(androidRoot, "app/src/main/res/layout/fragment_home.xml")
        assertTrue("fragment_home.xml 应该存在", layout.exists())
    }

    @Test
    fun test_27_2_dialog_utils_exists() {
        val utils = File(androidRoot, "app/src/main/java/com/weightloss/betting/util/DialogUtils.kt")
        assertTrue("DialogUtils.kt 应该存在", utils.exists())
        
        val content = utils.readText()
        assertTrue("应该有 showLoadingDialog 方法", content.contains("showLoadingDialog"))
        assertTrue("应该有 showErrorDialog 方法", content.contains("showErrorDialog"))
        assertTrue("应该有 showConfirmDialog 方法", content.contains("showConfirmDialog"))
    }

    @Test
    fun test_27_3_material_design_dependencies() {
        val buildGradle = File(androidRoot, "app/build.gradle")
        val content = buildGradle.readText()
        
        assertTrue("应该包含 Material Design 依赖", 
            content.contains("com.google.android.material:material"))
    }

    // ==================== 文档测试 ====================

    @Test
    fun test_implementation_summary_exists() {
        val summary = File(androidRoot, "TASKS_25-27_IMPLEMENTATION_SUMMARY.md")
        assertTrue("TASKS_25-27_IMPLEMENTATION_SUMMARY.md 应该存在", summary.exists())
    }

    @Test
    fun test_firebase_setup_guide_exists() {
        val guide = File(androidRoot, "FIREBASE_SETUP_GUIDE.md")
        assertTrue("FIREBASE_SETUP_GUIDE.md 应该存在", guide.exists())
    }

    @Test
    fun test_remaining_work_guide_exists() {
        val guide = File(androidRoot, "REMAINING_WORK_GUIDE.md")
        assertTrue("REMAINING_WORK_GUIDE.md 应该存在", guide.exists())
    }

    // ==================== 综合测试 ====================

    @Test
    fun test_all_key_files_exist() {
        val keyFiles = listOf(
            // 通知功能
            "app/src/main/java/com/weightloss/betting/service/FCMService.kt",
            "app/src/main/java/com/weightloss/betting/data/repository/NotificationRepository.kt",
            "app/src/main/java/com/weightloss/betting/util/NotificationPermissionHelper.kt",
            
            // 社交功能
            "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardActivity.kt",
            "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardViewModel.kt",
            "app/src/main/java/com/weightloss/betting/ui/social/BadgesActivity.kt",
            "app/src/main/java/com/weightloss/betting/ui/social/BadgesViewModel.kt",
            
            // UI/UX
            "app/src/main/java/com/weightloss/betting/ui/MainActivity.kt",
            "app/src/main/java/com/weightloss/betting/ui/main/HomeFragment.kt",
            "app/src/main/java/com/weightloss/betting/util/DialogUtils.kt"
        )
        
        val missingFiles = mutableListOf<String>()
        keyFiles.forEach { path ->
            val file = File(androidRoot, path)
            if (!file.exists()) {
                missingFiles.add(path)
            }
        }
        
        assertTrue("以下关键文件缺失: $missingFiles", missingFiles.isEmpty())
    }

    @Test
    fun test_social_repository_has_all_methods() {
        val repo = File(androidRoot, "app/src/main/java/com/weightloss/betting/data/repository/SocialRepository.kt")
        assertTrue("SocialRepository.kt 应该存在", repo.exists())
        
        val content = repo.readText()
        assertTrue("应该有 getLeaderboard 方法", content.contains("getLeaderboard"))
        assertTrue("应该有 getBadges 方法", content.contains("getBadges"))
        assertTrue("应该有 getComments 方法", content.contains("getComments"))
        assertTrue("应该有 postComment 方法", content.contains("postComment"))
        assertTrue("应该有 encourageUser 方法", content.contains("encourageUser"))
    }

    @Test
    fun test_api_service_has_social_endpoints() {
        val apiService = File(androidRoot, "app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt")
        val content = apiService.readText()
        
        // 排行榜 API
        assertTrue("应该有排行榜 API", content.contains("leaderboard"))
        
        // 勋章 API
        assertTrue("应该有勋章 API", content.contains("badges"))
        
        // 评论 API
        assertTrue("应该有评论 API", content.contains("comments"))
        
        // 鼓励 API
        assertTrue("应该有鼓励 API", content.contains("encourage"))
    }

    @Test
    fun test_notification_api_exists() {
        val apiService = File(androidRoot, "app/src/main/java/com/weightloss/betting/data/remote/ApiService.kt")
        val content = apiService.readText()
        
        assertTrue("应该有注册设备令牌 API", 
            content.contains("registerDeviceToken") || content.contains("register"))
    }

    // ==================== 架构测试 ====================

    @Test
    fun test_mvvm_architecture_followed() {
        // 检查 ViewModel 文件
        val viewModels = listOf(
            "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardViewModel.kt",
            "app/src/main/java/com/weightloss/betting/ui/social/BadgesViewModel.kt"
        )
        
        viewModels.forEach { path ->
            val file = File(androidRoot, path)
            assertTrue("$path 应该存在", file.exists())
            val content = file.readText()
            assertTrue("$path 应该继承 ViewModel", content.contains("ViewModel"))
            assertTrue("$path 应该使用 LiveData 或 StateFlow", 
                content.contains("LiveData") || content.contains("StateFlow"))
        }
    }

    @Test
    fun test_hilt_dependency_injection_used() {
        val activities = listOf(
            "app/src/main/java/com/weightloss/betting/ui/social/LeaderboardActivity.kt",
            "app/src/main/java/com/weightloss/betting/ui/social/BadgesActivity.kt"
        )
        
        activities.forEach { path ->
            val file = File(androidRoot, path)
            if (file.exists()) {
                val content = file.readText()
                assertTrue("$path 应该使用 @AndroidEntryPoint", 
                    content.contains("@AndroidEntryPoint"))
            }
        }
    }

    @Test
    fun test_repository_pattern_used() {
        val repositories = listOf(
            "app/src/main/java/com/weightloss/betting/data/repository/NotificationRepository.kt",
            "app/src/main/java/com/weightloss/betting/data/repository/SocialRepository.kt"
        )
        
        repositories.forEach { path ->
            val file = File(androidRoot, path)
            assertTrue("$path 应该存在", file.exists())
            val content = file.readText()
            assertTrue("$path 应该使用 @Singleton", content.contains("@Singleton"))
        }
    }
}
