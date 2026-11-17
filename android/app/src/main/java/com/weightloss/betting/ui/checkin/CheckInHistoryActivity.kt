package com.weightloss.betting.ui.checkin

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.weightloss.betting.databinding.ActivityCheckInHistoryBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CheckInHistoryActivity : BaseActivity() {
    private lateinit var binding: ActivityCheckInHistoryBinding
    private val viewModel: CheckInHistoryViewModel by viewModels()
    private val adapter = CheckInHistoryAdapter()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCheckInHistoryBinding.inflate(layoutInflater)
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
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
        binding.recyclerView.adapter = adapter
        binding.btnRetry.setOnClickListener { viewModel.load(planId) }
        viewModel.state.observe(this) { render(it) }
        viewModel.load(planId)
    }

    private fun render(state: CheckInHistoryState) {
        when (state) {
            is CheckInHistoryState.Loading -> {
                binding.progressBar.visibility = View.VISIBLE
                binding.recyclerView.visibility = View.GONE
                binding.emptyState.visibility = View.GONE
                binding.errorState.visibility = View.GONE
            }
            is CheckInHistoryState.Success -> {
                binding.progressBar.visibility = View.GONE
                binding.errorState.visibility = View.GONE
                adapter.submitList(state.items)
                val hasItems = state.items.isNotEmpty()
                binding.recyclerView.visibility = if (hasItems) View.VISIBLE else View.GONE
                binding.emptyState.visibility = if (hasItems) View.GONE else View.VISIBLE
            }
            is CheckInHistoryState.Error -> {
                binding.progressBar.visibility = View.GONE
                binding.recyclerView.visibility = View.GONE
                binding.emptyState.visibility = View.GONE
                binding.errorState.visibility = View.VISIBLE
                binding.tvError.text = state.message
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
