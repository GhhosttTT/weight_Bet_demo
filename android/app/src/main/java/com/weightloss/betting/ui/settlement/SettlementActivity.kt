package com.weightloss.betting.ui.settlement

import android.os.Bundle
import android.view.View
import android.widget.Toast
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
        viewModel.state.observe(this) { render(it) }
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
                setChoiceEnabled(false)
            }
            is SettlementState.Ready -> {
                binding.progressBar.visibility = View.GONE
                updateStatus(state.status)
                binding.btnSubmit.isEnabled = !state.status.settlementCompleted && !state.status.inArbitration
                setChoiceEnabled(!state.status.currentUserSubmitted && !state.status.settlementCompleted && !state.status.inArbitration)
            }
            is SettlementState.Submitted -> {
                binding.progressBar.visibility = View.GONE
                binding.btnSubmit.isEnabled = false
                setChoiceEnabled(false)
                if (state.status != null) {
                    updateStatus(state.status)
                } else {
                    binding.tvStatus.text = "结算选择已提交，状态刷新失败，请返回后重新打开"
                }
                Toast.makeText(this, "结算选择已提交，等待对手确认", Toast.LENGTH_SHORT).show()
            }
            is SettlementState.Error -> {
                binding.progressBar.visibility = View.GONE
                binding.btnSubmit.isEnabled = true
                setChoiceEnabled(true)
                Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun updateStatus(status: SettlementSelectionStatus) {
        binding.tvRound.text = "第 ${status.currentRound} 轮"
        // 服务端只返回双方提交标记；按钮在提交后由当前页面锁定，状态文案仍以双方标记为准。
        binding.tvStatus.text = when {
            status.settlementCompleted -> "结算已完成"
            status.inArbitration -> "双方多轮选择不一致，已进入仲裁"
            status.creatorSubmitted && status.participantSubmitted -> "双方已提交，系统正在匹配结果"
            status.creatorSubmitted || status.participantSubmitted -> "一方已提交，等待另一方提交"
            else -> "请选择双方成果后提交"
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
