package com.weightloss.betting.ui

import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Toast
import com.google.firebase.messaging.FirebaseMessaging
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.weightloss.betting.R
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.model.DoubleCheckItem
import com.weightloss.betting.data.model.InvitationItem
import com.weightloss.betting.data.model.SettlementItem
import com.weightloss.betting.data.repository.AuthRepository
import com.weightloss.betting.data.repository.BettingPlanRepository
import com.weightloss.betting.data.repository.NotificationRepository
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.ActivityMainBinding
import com.weightloss.betting.ui.checkin.CheckInActivity
import com.weightloss.betting.ui.main.HomeFragment
import com.weightloss.betting.ui.main.CoachFragment
import com.weightloss.betting.ui.plan.PlanDetailActivity
import com.weightloss.betting.ui.plan.PlanListActivity
import com.weightloss.betting.ui.plan.PlanListFragment
import com.weightloss.betting.ui.profile.ProfileActivity
import com.weightloss.betting.ui.profile.ProfileFragment
import com.weightloss.betting.ui.settlement.SettlementActivity
import com.weightloss.betting.util.EdgeSwipeBackHelper
import com.weightloss.betting.util.NotificationPermissionHelper
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 主 Activity - 带底部导航
 */
@AndroidEntryPoint
class MainActivity : AppCompatActivity() {

    companion object {
        private const val PREF_NOTIFICATION_PERMISSION_REQUESTED = "notification_permission_requested"
    }
    
    @Inject
    lateinit var authRepository: AuthRepository
    
    @Inject
    lateinit var bettingPlanRepository: BettingPlanRepository
    
    @Inject
    lateinit var tokenManager: TokenManager

    @Inject
    lateinit var notificationRepository: NotificationRepository
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var prefs: SharedPreferences
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // 初始化 SharedPreferences（用于记录已显示的弹窗）
        prefs = getSharedPreferences("main_activity_prefs", MODE_PRIVATE)
        requestNotificationPermissionIfNeeded()
        
        setupBottomNavigation()
        registerCurrentPushToken()
        
        // 默认显示首页
        if (savedInstanceState == null) {
            loadFragment(HomeFragment())
        }
        
        // 处理通知点击跳转
        handleNotificationIntent(intent)
        
        // 启用边缘滑动返回
        EdgeSwipeBackHelper.enableForFragmentActivity(this)
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (prefs.getBoolean(PREF_NOTIFICATION_PERMISSION_REQUESTED, false)) return
        prefs.edit().putBoolean(PREF_NOTIFICATION_PERMISSION_REQUESTED, true).apply()
        if (!NotificationPermissionHelper.hasNotificationPermission(this)) {
            NotificationPermissionHelper.requestNotificationPermission(this)
        }
    }

    override fun onResume() {
        super.onResume()
        // 与 iOS 前台恢复行为一致：返回主页面时重新拉取待处理操作，
        // 避免用户在弹窗处理后仍看不到下一条邀请或结算提醒。
        checkPendingActions()
    }

    private fun registerCurrentPushToken() {
        FirebaseMessaging.getInstance().token.addOnCompleteListener { task ->
            if (!task.isSuccessful || task.result.isNullOrBlank()) return@addOnCompleteListener
            CoroutineScope(Dispatchers.IO).launch {
                notificationRepository.registerDeviceToken(task.result)
            }
        }
    }
    
    private fun setupBottomNavigation() {
        binding.bottomNavigation.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.navigation_home -> {
                    loadFragment(HomeFragment())
                    true
                }
                R.id.navigation_coach -> {
                    loadFragment(CoachFragment())
                    true
                }
                R.id.navigation_plans -> {
                    loadFragment(PlanListFragment())
                    true
                }
                R.id.navigation_profile -> {
                    loadFragment(ProfileFragment())
                    true
                }
                else -> false
            }
        }
    }
    
    private fun loadFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.navHostFragment, fragment)
            .commit()
    }
    
    private fun handleNotificationIntent(intent: Intent?) {
        intent?.let {
            val notificationType = it.getStringExtra("notification_type")
            val relatedId = it.getStringExtra("related_id")
            
            when (notificationType) {
                "invite", "plan_active" -> {
                    if (!relatedId.isNullOrBlank()) {
                        startActivity(Intent(this, PlanDetailActivity::class.java).apply {
                            putExtra("PLAN_ID", relatedId)
                        })
                    }
                }
                "settlement" -> {
                    if (!relatedId.isNullOrBlank()) {
                        startActivity(Intent(this, SettlementActivity::class.java).apply {
                            putExtra("PLAN_ID", relatedId)
                        })
                    }
                }
                "check_in_reminder" -> {
                    startActivity(Intent(this, CheckInActivity::class.java).apply {
                        if (!relatedId.isNullOrBlank()) putExtra("PLAN_ID", relatedId)
                    })
                }
            }
        }
    }
    
    private fun checkIn() {
        val intent = Intent(this, CheckInActivity::class.java)
        startActivity(intent)
    }
    
    private fun checkPendingActions() {
        CoroutineScope(Dispatchers.Main).launch {
            val result = authRepository.getPendingActions()
            if (result is NetworkResult.Success) {
                val pendingActions = result.data
                // 如果有邀请，显示邀请弹窗（只显示一次）
                pendingActions.invitations.firstOrNull { invitation ->
                    !prefs.getBoolean("invitation_shown_${invitation.id}", false)
                }?.let { invitation ->
                    val shownKey = "invitation_shown_${invitation.id}"
                    showInvitationDialog(invitation, shownKey)
                }
                // 如果有 Double Check，显示确认弹窗（只显示一次）
                pendingActions.doubleChecks.firstOrNull { doubleCheck ->
                    !prefs.getBoolean("doublecheck_shown_${doubleCheck.planId}", false)
                }?.let { doubleCheck ->
                    val shownKey = "doublecheck_shown_${doubleCheck.planId}"
                    showDoubleCheckDialog(doubleCheck, shownKey)
                }
                // 如果有待结算的计划，显示结算弹窗（只显示一次）
                pendingActions.settlements.firstOrNull { settlement ->
                    !prefs.getBoolean("settlement_shown_${settlement.planId}", false)
                }?.let { settlement ->
                    val shownKey = "settlement_shown_${settlement.planId}"
                    showSettlementDialog(settlement, shownKey)
                }
            } else if (result is NetworkResult.Error) {
                // 非致命错误，仅记录日志
                android.util.Log.w("MainActivity", "Failed to get pending actions")
            }
        }
    }
    
    private fun showInvitationDialog(invitation: InvitationItem, shownKey: String) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("收到邀请")
            .setMessage(invitation.message ?: "你收到一个对赌计划邀请")
            .setPositiveButton("查看详情") { _, _ ->
                // 标记为已显示
                prefs.edit().putBoolean(shownKey, true).apply()
                // 跳转到计划详情页
                val intent = Intent(this, PlanDetailActivity::class.java)
                intent.putExtra("PLAN_ID", invitation.planId)
                startActivity(intent)
            }
            .setNegativeButton("稍后再说") { _, _ ->
                // 标记为已显示
                prefs.edit().putBoolean(shownKey, true).apply()
            }
            .show()
    }
    
    private fun showDoubleCheckDialog(doubleCheck: DoubleCheckItem, shownKey: String) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("需要确认计划")
            .setMessage("参与者已提交目标，请确认计划是否生效")
            .setPositiveButton("去确认") { _, _ ->
                // 标记为已显示
                prefs.edit().putBoolean(shownKey, true).apply()
                // 跳转到计划详情页进行确认
                val intent = Intent(this, PlanDetailActivity::class.java)
                intent.putExtra("PLAN_ID", doubleCheck.planId)
                startActivity(intent)
            }
            .setNegativeButton("稍后再说") { _, _ ->
                // 标记为已显示
                prefs.edit().putBoolean(shownKey, true).apply()
            }
            .show()
    }
    
    private fun showSettlementDialog(settlement: SettlementItem, shownKey: String) {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("计划结算提醒")
            .setMessage("您的对赌计划已到期，请前往进行结算")
            .setPositiveButton("去结算") { _, _ ->
                // 标记为已显示
                prefs.edit().putBoolean(shownKey, true).apply()
                // 跳转到独立结算页
                val intent = Intent(this, SettlementActivity::class.java)
                intent.putExtra("PLAN_ID", settlement.planId)
                startActivity(intent)
            }
            .setNegativeButton("稍后再说") { _, _ ->
                // 标记为已显示
                prefs.edit().putBoolean(shownKey, true).apply()
            }
            .show()
    }
}
