package com.weightloss.betting.ui

import android.app.AlertDialog
import android.content.Intent
import android.content.SharedPreferences
import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.fragment.app.Fragment
import com.google.android.material.bottomnavigation.BottomNavigationView
import com.weightloss.betting.R
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.model.BettingPlan
import com.weightloss.betting.data.model.DoubleCheckItem
import com.weightloss.betting.data.model.InvitationItem
import com.weightloss.betting.data.model.SettlementItem
import com.weightloss.betting.data.repository.AuthRepository
import com.weightloss.betting.data.repository.BettingPlanRepository
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
import com.weightloss.betting.util.EdgeSwipeBackHelper
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
    
    @Inject
    lateinit var authRepository: AuthRepository
    
    @Inject
    lateinit var bettingPlanRepository: BettingPlanRepository
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private lateinit var binding: ActivityMainBinding
    private lateinit var prefs: SharedPreferences
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        // 初始化 SharedPreferences（用于记录已显示的弹窗）
        prefs = getSharedPreferences("main_activity_prefs", MODE_PRIVATE)
        
        setupBottomNavigation()
        
        // 默认显示首页
        if (savedInstanceState == null) {
            loadFragment(HomeFragment())
        }
        
        // 处理通知点击跳转
        handleNotificationIntent(intent)
        
        // 检查待处理操作
        checkPendingActions()
        
        // 启用边缘滑动返回
        EdgeSwipeBackHelper.enableForFragmentActivity(this)
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
            
            // TODO: 根据通知类型跳转到相应页面
            when (notificationType) {
                "invite", "plan_active" -> {
                    // 跳转到计划详情
                }
                "settlement" -> {
                    // 跳转到结算详情
                }
                "check_in_reminder" -> {
                    // 跳转到打卡页面
                }
            }
        }
    }
    
    private fun checkIn() {
        CoroutineScope(Dispatchers.Main).launch {
            val userId = tokenManager.getUserId()
            if (userId == null) {
                Toast.makeText(this@MainActivity, "请先登录", Toast.LENGTH_SHORT).show()
                return@launch
            }
            
            when (val result = bettingPlanRepository.getUserPlans(userId, "active", forceRefresh = true)) {
                is NetworkResult.Success -> {
                    val activePlans = result.data
                    when {
                        activePlans.isEmpty() -> {
                            Toast.makeText(this@MainActivity, "没有进行中的计划", Toast.LENGTH_SHORT).show()
                        }
                        activePlans.size == 1 -> {
                            startCheckInActivity(activePlans[0].id)
                        }
                        else -> {
                            showPlanSelectionDialog(activePlans)
                        }
                    }
                }
                is NetworkResult.Error -> {
                    Toast.makeText(this@MainActivity, "获取计划列表失败: ${result.exception.message}", Toast.LENGTH_SHORT).show()
                }
                else -> {}
            }
        }
    }
    
    private fun showPlanSelectionDialog(plans: List<BettingPlan>) {
        val planNames = plans.map { plan ->
            val creatorName = plan.creatorNickname ?: plan.creatorEmail ?: "创建者"
            val participantName = plan.participantNickname ?: plan.participantEmail ?: "参与者"
            "$creatorName vs $participantName"
        }.toTypedArray()
        
        AlertDialog.Builder(this)
            .setTitle("选择要打卡的计划")
            .setItems(planNames) { _, which ->
                startCheckInActivity(plans[which].id)
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    private fun startCheckInActivity(planId: String) {
        val intent = Intent(this, CheckInActivity::class.java)
        intent.putExtra("PLAN_ID", planId)
        startActivity(intent)
    }
    
    private fun checkPendingActions() {
        CoroutineScope(Dispatchers.Main).launch {
            when (val result = authRepository.getPendingActions()) {
                is NetworkResult.Success -> {
                    val pendingActions = result.data
                    // 如果有邀请，显示邀请弹窗（只显示一次）
                    if (pendingActions.invitations.isNotEmpty()) {
                        val invitation = pendingActions.invitations.first()
                        val shownKey = "invitation_shown_${invitation.id}"
                        if (!prefs.getBoolean(shownKey, false)) {
                            showInvitationDialog(invitation, shownKey)
                        }
                    }
                    // 如果有 Double Check，显示确认弹窗（只显示一次）
                    if (pendingActions.doubleChecks.isNotEmpty()) {
                        val doubleCheck = pendingActions.doubleChecks.first()
                        val shownKey = "doublecheck_shown_${doubleCheck.planId}"
                        if (!prefs.getBoolean(shownKey, false)) {
                            showDoubleCheckDialog(doubleCheck, shownKey)
                        }
                    }
                    // 如果有待结算的计划，显示结算弹窗（只显示一次）
                    if (pendingActions.settlements.isNotEmpty()) {
                        val settlement = pendingActions.settlements.first()
                        val shownKey = "settlement_shown_${settlement.planId}"
                        if (!prefs.getBoolean(shownKey, false)) {
                            showSettlementDialog(settlement, shownKey)
                        }
                    }
                }
                is NetworkResult.Error -> {
                    // 非致命错误，仅记录日志
                    android.util.Log.w("MainActivity", "Failed to get pending actions: ${result.exception.message}")
                }
                else -> {}
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
                // 跳转到计划详情页进行结算
                val intent = Intent(this, PlanDetailActivity::class.java)
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
