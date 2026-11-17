package com.weightloss.betting.ui.checkin

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.weightloss.betting.data.model.ProgressStats
import com.weightloss.betting.databinding.ActivityProgressBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint
import java.util.Locale

@AndroidEntryPoint
class ProgressActivity : BaseActivity() {
    private lateinit var binding: ActivityProgressBinding
    private val viewModel: ProgressViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProgressBinding.inflate(layoutInflater)
        setContentView(binding.root)
        val planId = intent.getStringExtra("PLAN_ID")
        if (planId.isNullOrBlank()) {
            Toast.makeText(this, "计划 ID 无效", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }
        viewModel.state.observe(this) { render(it) }
        viewModel.load(planId)
    }

    private fun render(state: ProgressState) {
        when (state) {
            is ProgressState.Loading -> binding.progressBar.visibility = View.VISIBLE
            is ProgressState.Success -> {
                binding.progressBar.visibility = View.GONE
                renderStats(state.stats)
            }
            is ProgressState.Error -> {
                binding.progressBar.visibility = View.GONE
                Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun renderStats(stats: ProgressStats) {
        val percent = stats.progressPercentage.coerceIn(0.0, 100.0)
        binding.progressWeight.progress = percent.toInt()
        binding.tvProgressPercent.text = String.format(Locale.CHINA, "%.1f%% 已完成", percent)
        binding.tvCurrentWeight.text = String.format(Locale.CHINA, "当前体重  %.1f kg", stats.currentWeight)
        binding.tvInitialWeight.text = String.format(Locale.CHINA, "初始体重\n%.1f kg", stats.initialWeight)
        binding.tvTargetWeight.text = String.format(Locale.CHINA, "目标体重\n%.1f kg", stats.targetWeight)
        binding.tvWeightLoss.text = String.format(Locale.CHINA, "已减重\n%.1f kg", stats.weightLoss)
        binding.tvCheckInCount.text = "打卡次数\n${stats.checkInCount} 次"
        binding.tvDaysRemaining.text = "剩余天数  ${stats.daysRemaining} 天"
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
