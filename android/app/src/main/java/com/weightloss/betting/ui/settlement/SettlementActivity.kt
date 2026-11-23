package com.weightloss.betting.ui.settlement

import android.os.Bundle
import android.text.InputType
import android.view.Gravity
import android.view.View
import android.widget.EditText
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.activity.viewModels
import com.weightloss.betting.data.model.SettlementSelectionStatus
import com.weightloss.betting.databinding.ActivitySettlementBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class SettlementActivity : BaseActivity() {
    private lateinit var binding: ActivitySettlementBinding
    private val viewModel: SettlementViewModel by viewModels()
    private var planId: String? = null
    private var latestStatus: SettlementSelectionStatus? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettlementBinding.inflate(layoutInflater)
        setContentView(binding.root)
        planId = intent.getStringExtra("PLAN_ID")
        if (planId.isNullOrBlank()) {
            Toast.makeText(this, "计划 ID 无效", Toast.LENGTH_SHORT).show()
            finish()
            return
        }

        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.btnSubmit.setOnClickListener { submit() }
        binding.btnDispute.setOnClickListener { showDisputeDialog() }
        viewModel.state.observe(this) { render(it) }
        viewModel.disputeState.observe(this) { renderDispute(it) }
        viewModel.load(planId!!)
    }

    private fun submit() {
        val selfSelected = when (binding.rgSelf.checkedRadioButtonId) {
            binding.rbSelfAchieved.id -> true
            binding.rbSelfNotAchieved.id -> false
            else -> null
        }
        val opponentSelected = when (binding.rgOpponent.checkedRadioButtonId) {
            binding.rbOpponentAchieved.id -> true
            binding.rbOpponentNotAchieved.id -> false
            else -> null
        }
        if (selfSelected == null || opponentSelected == null) {
            Toast.makeText(this, "请先选择双方成果", Toast.LENGTH_SHORT).show()
            return
        }
        viewModel.submit(planId!!, selfSelected, opponentSelected)
    }

    private fun render(state: SettlementState) {
        when (state) {
            is SettlementState.Loading -> {
                binding.progressBar.visibility = View.VISIBLE
                binding.btnSubmit.isEnabled = false
                binding.btnDispute.visibility = View.GONE
                binding.tvDisputeStatus.visibility = View.GONE
                setChoiceEnabled(false)
            }
            is SettlementState.Ready -> {
                binding.progressBar.visibility = View.GONE
                updateStatus(state.status)
                updateDisputeUI(state.status)
                binding.btnSubmit.isEnabled = !state.status.settlementCompleted && !state.status.inArbitration
                setChoiceEnabled(!state.status.currentUserSubmitted && !state.status.settlementCompleted && !state.status.inArbitration)
            }
            is SettlementState.Submitted -> {
                binding.progressBar.visibility = View.GONE
                binding.btnSubmit.isEnabled = false
                setChoiceEnabled(false)
                if (state.status != null) {
                    updateStatus(state.status)
                    updateDisputeUI(state.status)
                } else {
                    binding.tvStatus.text = "结算选择已提交，状态刷新失败，请返回后重新打开"
                }
                Toast.makeText(this, "结算选择已提交，等待对手确认", Toast.LENGTH_SHORT).show()
            }
            is SettlementState.Error -> {
                binding.progressBar.visibility = View.GONE
                binding.btnSubmit.isEnabled = true
                binding.btnDispute.visibility = View.GONE
                binding.tvDisputeStatus.visibility = View.GONE
                setChoiceEnabled(true)
                Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun updateStatus(status: SettlementSelectionStatus) {
        latestStatus = status
        binding.tvRound.text = "第 ${status.currentRound} 轮"
        binding.tvStatus.text = when {
            status.settlementCompleted -> "结算已完成"
            status.inArbitration -> "双方多轮选择不一致，已进入仲裁"
            status.matched -> "双方选择已匹配，等待系统结算"
            status.creatorSubmitted && status.participantSubmitted -> "双方已提交，系统正在匹配结果"
            status.creatorSubmitted || status.participantSubmitted -> "一方已提交，等待另一方提交"
            else -> "请选择双方成果后提交"
        }
    }

    private fun updateDisputeUI(status: SettlementSelectionStatus) {
        val settlementId = status.settlementId
        if (!status.settlementCompleted || settlementId.isNullOrBlank()) {
            binding.btnDispute.visibility = View.GONE
            binding.tvDisputeStatus.visibility = View.GONE
            return
        }

        binding.btnDispute.visibility = View.VISIBLE
        binding.tvDisputeStatus.visibility = View.VISIBLE
        val disputeStatus = status.disputeStatus
        if (disputeStatus.isNullOrBlank()) {
            binding.btnDispute.isEnabled = true
            binding.btnDispute.text = "反馈结算问题"
            binding.tvDisputeStatus.text = "对结算结果有疑问？可提交争议，后台审核后会更新状态。"
        } else {
            binding.btnDispute.isEnabled = false
            binding.btnDispute.text = "争议已提交"
            val label = mapOf(
                "pending" to "待处理",
                "under_review" to "审核中",
                "resolved" to "已解决",
                "rejected" to "已拒绝"
            )[disputeStatus] ?: disputeStatus
            val notes = status.disputeAdminNotes?.takeIf { it.isNotBlank() }
                ?.let { "\n管理员备注：$it" } ?: ""
            binding.tvDisputeStatus.text = "争议状态：$label$notes"
        }
    }

    private fun showDisputeDialog() {
        val settlementId = latestStatus?.settlementId ?: return
        val input = EditText(this).apply {
            hint = "请描述结算问题（至少10个字）"
            minLines = 4
            gravity = Gravity.TOP
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_FLAG_MULTI_LINE
        }
        val dialog = AlertDialog.Builder(this)
            .setTitle("反馈结算问题")
            .setView(input)
            .setNegativeButton("取消", null)
            .setPositiveButton("提交", null)
            .create()
        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                val reason = input.text.toString().trim()
                if (reason.length < 10) {
                    input.error = "至少填写10个字"
                    return@setOnClickListener
                }
                dialog.dismiss()
                viewModel.submitDispute(settlementId, reason)
            }
        }
        dialog.show()
    }

    private fun renderDispute(state: DisputeState) {
        when (state) {
            DisputeState.Idle -> Unit
            DisputeState.Submitting -> {
                binding.btnDispute.isEnabled = false
                binding.btnDispute.text = "提交中…"
            }
            is DisputeState.Success -> {
                binding.btnDispute.isEnabled = false
                binding.btnDispute.text = "争议已提交"
                binding.tvDisputeStatus.visibility = View.VISIBLE
                binding.tvDisputeStatus.text = "争议状态：待处理"
                planId?.let { viewModel.load(it) }
            }
            is DisputeState.Error -> {
                binding.btnDispute.isEnabled = true
                binding.btnDispute.text = "反馈结算问题"
                Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun setChoiceEnabled(enabled: Boolean) {
        binding.rgSelf.isEnabled = enabled
        binding.rgOpponent.isEnabled = enabled
        for (index in 0 until binding.rgSelf.childCount) {
            binding.rgSelf.getChildAt(index).isEnabled = enabled
        }
        for (index in 0 until binding.rgOpponent.childCount) {
            binding.rgOpponent.getChildAt(index).isEnabled = enabled
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
