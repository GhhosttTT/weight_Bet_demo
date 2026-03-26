package com.weightloss.betting.ui.plan

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.weightloss.betting.databinding.ActivityPlanDetailBinding
import com.weightloss.betting.ui.checkin.CheckInActivity
import dagger.hilt.android.AndroidEntryPoint
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class PlanDetailActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityPlanDetailBinding
    private val viewModel: PlanDetailViewModel by viewModels()
    private val abandonViewModel: AbandonPlanViewModel by viewModels()
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private var planId: String? = null
    private var planStatus: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlanDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        planId = intent.getStringExtra("PLAN_ID")
        
        if (planId == null) {
            Toast.makeText(this, "计划ID无效", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        setupToolbar()
        setupObservers()
        setupAbandonObservers()
        setupListeners()
        
        // 强制从服务器刷新，获取最新的用户信息
        viewModel.loadPlanDetail(planId!!, forceRefresh = true)
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupObservers() {
        viewModel.planDetailState.observe(this) { state ->
            when (state) {
                is PlanDetailState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.layoutContent.visibility = View.GONE
                }
                is PlanDetailState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.layoutContent.visibility = View.VISIBLE
                    displayPlanDetail(state.plan)
                    planStatus = state.plan.status
                }
                is PlanDetailState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        
        viewModel.acceptPlanState.observe(this) { state ->
            when (state) {
                is AcceptPlanState.Idle -> {
                    // Do nothing
                }
                is AcceptPlanState.Loading -> {
                    binding.btnAccept.isEnabled = false
                    binding.btnReject.isEnabled = false
                }
                is AcceptPlanState.Success -> {
                    // 接受成功后不立刻关闭界面，刷新计划详情以展示参与者信息并告知用户等待创建者确认
                    Toast.makeText(this, "参与申请已提交，等待创建者确认", Toast.LENGTH_SHORT).show()
                    planId?.let { id ->
                        // 先隐藏接受/拒绝按钮区域
                        binding.layoutAcceptPlan.visibility = View.GONE
                        // 刷新计划详情
                        viewModel.loadPlanDetail(id, forceRefresh = true)
                    }
                }
                is AcceptPlanState.PaymentRequired -> {
                    binding.btnAccept.isEnabled = true
                    binding.btnReject.isEnabled = true
                    // 调起充值界面
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                    planId?.let { id ->
                        val intent = Intent(this, com.weightloss.betting.ui.payment.ChargeActivity::class.java)
                        intent.putExtra("required_amount", state.requiredAmount)
                        intent.putExtra("plan_id", id)
                        startActivity(intent)
                    }
                }
                is AcceptPlanState.Error -> {
                    binding.btnAccept.isEnabled = true
                    binding.btnReject.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        
        viewModel.revokePlanState.observe(this) { state ->
            when (state) {
                is RevokePlanState.Idle -> {
                    // Do nothing
                }
                is RevokePlanState.Loading -> {
                    binding.btnRevokePlan.isEnabled = false
                }
                is RevokePlanState.Success -> {
                    Toast.makeText(this, "计划已撤销，赌金已退还", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is RevokePlanState.Error -> {
                    binding.btnRevokePlan.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        
        viewModel.confirmPlanState.observe(this) { state ->
            when (state) {
                is ConfirmPlanState.Idle -> {
                    // Do nothing
                }
                is ConfirmPlanState.Loading -> {
                    binding.btnConfirmPlan.isEnabled = false
                    binding.btnRejectParticipant.isEnabled = false
                }
                is ConfirmPlanState.Success -> {
                    Toast.makeText(this, "计划已生效", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is ConfirmPlanState.Error -> {
                    binding.btnConfirmPlan.isEnabled = true
                    binding.btnRejectParticipant.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        
        setupAbandonObservers()
    }
    
    private fun setupAbandonObservers() {
        abandonViewModel.abandonState.observe(this) { state ->
            when (state) {
                is AbandonState.Loading -> {
                    binding.btnAbandonPlan.isEnabled = false
                }
                is AbandonState.Success -> {
                    Toast.makeText(this, state.result.message, Toast.LENGTH_SHORT).show()
                    finish()
                }
                is AbandonState.Error -> {
                    binding.btnAbandonPlan.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun displayPlanDetail(plan: com.weightloss.betting.data.model.BettingPlan) {
        binding.tvStatus.text = when (plan.status) {
            "pending" -> "待接受"
            "waiting_double_check" -> "待二次确认"
            "active" -> "进行中"
            "completed" -> "已完成"
            "cancelled" -> "已取消"
            "rejected" -> "已拒绝"
            "expired" -> "已过期"
            else -> plan.status
        }
        
        binding.tvBetAmount.text = "¥${plan.betAmount}"
        binding.tvDateRange.text = "${dateFormat.format(plan.startDate)} 至 ${dateFormat.format(plan.endDate)}"
        
        // Display creator info
        binding.tvCreatorNickname.text = plan.creatorNickname ?: "未知用户"
        binding.tvCreatorEmail.text = plan.creatorEmail ?: ""
        
        if (plan.creatorInitialWeight != null && plan.creatorTargetWeight != null) {
            val weightLoss = plan.creatorInitialWeight - plan.creatorTargetWeight
            binding.tvCreatorGoal.text = "${plan.creatorInitialWeight}kg → ${plan.creatorTargetWeight}kg (减重${weightLoss}kg)"
        } else {
            binding.tvCreatorGoal.text = "待设置"
        }
        
        // Display participant info if exists
        if (plan.participantId != null) {
            binding.tvParticipantLabel.visibility = View.VISIBLE
            binding.layoutParticipantInfo.visibility = View.VISIBLE
            
            binding.tvParticipantNickname.text = plan.participantNickname ?: "未知用户"
            binding.tvParticipantEmail.text = plan.participantEmail ?: ""
            
            if (plan.participantInitialWeight != null && plan.participantTargetWeight != null) {
                val weightLoss = plan.participantInitialWeight - plan.participantTargetWeight
                binding.tvParticipantGoal.text = "${plan.participantInitialWeight}kg → ${plan.participantTargetWeight}kg (减重${weightLoss}kg)"
            } else {
                binding.tvParticipantGoal.text = "待设置"
            }
        } else {
            binding.tvParticipantLabel.visibility = View.GONE
            binding.layoutParticipantInfo.visibility = View.GONE
        }
        
        binding.tvDescription.text = plan.description ?: "无描述"
        
        // Show check-in button ONLY for active plans
        if (plan.status == "active") {
            binding.btnCheckIn.visibility = View.VISIBLE
        } else {
            binding.btnCheckIn.visibility = View.GONE
        }
        
        // Show invite button for pending plans without participant (creator's view)
        val showInvite = intent.getBooleanExtra("SHOW_INVITE", false)
        if (plan.status == "pending" && plan.participantId == null && showInvite) {
            binding.btnInviteFriend.visibility = View.VISIBLE
        } else {
            binding.btnInviteFriend.visibility = View.GONE
        }
        
        // Show abandon button ONLY for active plans (not for pending plans)
        if (plan.status == "active") {
            binding.btnAbandonPlan.visibility = View.VISIBLE
            binding.btnAbandonPlan.text = "放弃计划 (失去赌金)"
        } else {
            binding.btnAbandonPlan.visibility = View.GONE
        }
        
        // Show revoke button for creator when plan is pending
        if (plan.status == "pending" && plan.creatorId == viewModel.getCurrentUserId()) {
            binding.btnRevokePlan.visibility = View.VISIBLE
        } else {
            binding.btnRevokePlan.visibility = View.GONE
        }
        
        // Show confirm/reject buttons for creator when participant has accepted
        if (plan.status == "waiting_double_check" && 
            plan.creatorId == viewModel.getCurrentUserId() && 
            plan.participantId != null) {
            binding.layoutConfirmPlan.visibility = View.VISIBLE
        } else {
            binding.layoutConfirmPlan.visibility = View.GONE
        }
        
        // Show accept/reject buttons for pending plans when current user is the participant (not creator)
        // participantId is null means the invitee hasn't accepted yet
        // Only show if current user is NOT the creator
        val isCreator = plan.creatorId == viewModel.getCurrentUserId()
        if (plan.status == "pending" && plan.participantId == null && !isCreator) {
            binding.layoutAcceptPlan.visibility = View.VISIBLE
        } else {
            binding.layoutAcceptPlan.visibility = View.GONE
        }
    }
    
    private fun setupListeners() {
        binding.btnCheckIn.setOnClickListener {
            planId?.let { id ->
                val intent = Intent(this, CheckInActivity::class.java)
                intent.putExtra("PLAN_ID", id)
                startActivity(intent)
            }
        }
        
        binding.btnInviteFriend.setOnClickListener {
            planId?.let { id ->
                InviteFriendDialog.newInstance(id).show(
                    supportFragmentManager,
                    "InviteFriendDialog"
                )
            }
        }
            
        binding.btnAbandonPlan.setOnClickListener {
            planId?.let { id ->
                planStatus?.let { status ->
                    showAbandonConfirmation(status)
                }
            }
        }
        
        binding.btnRevokePlan.setOnClickListener {
            planId?.let { id ->
                showRevokeConfirmation()
            }
        }
        
        binding.btnConfirmPlan.setOnClickListener {
            planId?.let { id ->
                viewModel.confirmPlan(id)
            }
        }
        
        binding.btnRejectParticipant.setOnClickListener {
            planId?.let { id ->
                viewModel.rejectPlan(id)
            }
        }
        
        binding.btnAccept.setOnClickListener {
            val initialWeight = binding.etParticipantInitialWeight.text.toString()
            val targetWeight = binding.etParticipantTargetWeight.text.toString()
            
            if (initialWeight.isBlank()) {
                Toast.makeText(this, "请输入初始体重", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            if (targetWeight.isBlank()) {
                Toast.makeText(this, "请输入目标体重", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            viewModel.acceptPlan(planId!!, initialWeight, targetWeight)
        }
        
        binding.btnReject.setOnClickListener {
            viewModel.rejectPlan(planId!!)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    /**
     * 显示放弃计划确认对话框
     */
    private fun showAbandonConfirmation(planStatus: String) {
        val message = if (planStatus == "pending") {
            "确定要放弃这个计划吗？\n\n放弃后您的赌金将全额退还。"
        } else {
            "确定要放弃这个进行中的计划吗？\n\n警告：放弃后您将失去赌金，对方将获得全部赌金！"
        }
        
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("确认放弃计划")
            .setMessage(message)
            .setIcon(android.R.drawable.ic_dialog_alert)
            .setNegativeButton("取消", null)
            .setPositiveButton("确定放弃") { _, _ ->
                planId?.let { id ->
                    abandonViewModel.abandonPlan(id, confirmation = true)
                }
            }
            .show()
    }
    
    /**
     * 显示撤销计划确认对话框
     */
    private fun showRevokeConfirmation() {
        val message = "确定要撤销这个计划吗？\n\n撤销后您和参与者的赌金都将全额退还。"
        
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("确认撤销计划")
            .setMessage(message)
            .setIcon(android.R.drawable.ic_dialog_alert)
            .setNegativeButton("取消", null)
            .setPositiveButton("确定撤销") { _, _ ->
                planId?.let { id ->
                    viewModel.revokePlan(id)
                }
            }
            .show()
    }
}
