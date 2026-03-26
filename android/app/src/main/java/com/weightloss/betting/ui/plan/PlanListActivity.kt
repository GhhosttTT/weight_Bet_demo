package com.weightloss.betting.ui.plan

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.weightloss.betting.R
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.ActivityPlanListBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class PlanListActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityPlanListBinding
    private val viewModel: PlanListViewModel by viewModels()
    private lateinit var adapter: PlanAdapter
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private var userId: String? = null
    private var currentStatus: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPlanListBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupRecyclerView()
        setupObservers()
        setupListeners()
        
        // Load user ID and plans
        lifecycleScope.launch {
            userId = tokenManager.getUserId()
            if (userId != null) {
                viewModel.loadPlans(userId!!)
            } else {
                Toast.makeText(this@PlanListActivity, "用户未登录", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
    
    private fun setupRecyclerView() {
        adapter = PlanAdapter { plan ->
            // Navigate to plan detail
            val intent = Intent(this, PlanDetailActivity::class.java)
            intent.putExtra("PLAN_ID", plan.id)
            startActivity(intent)
        }
        
        binding.recyclerViewPlans.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewPlans.adapter = adapter
    }
    
    private fun setupObservers() {
        viewModel.planListState.observe(this) { state ->
            when (state) {
                is PlanListState.Loading -> {
                    binding.swipeRefresh.isRefreshing = true
                    binding.tvEmptyState.visibility = View.GONE
                }
                is PlanListState.Success -> {
                    binding.swipeRefresh.isRefreshing = false
                    if (state.plans.isEmpty()) {
                        binding.tvEmptyState.visibility = View.VISIBLE
                        binding.recyclerViewPlans.visibility = View.GONE
                    } else {
                        binding.tvEmptyState.visibility = View.GONE
                        binding.recyclerViewPlans.visibility = View.VISIBLE
                        adapter.submitList(state.plans)
                    }
                }
                is PlanListState.Error -> {
                    binding.swipeRefresh.isRefreshing = false
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.swipeRefresh.setOnRefreshListener {
            userId?.let {
                viewModel.loadPlans(it, currentStatus, forceRefresh = true)
            }
        }
        
        binding.chipGroupStatus.setOnCheckedChangeListener { _, checkedId ->
            currentStatus = when (checkedId) {
                R.id.chipPending -> "pending"
                R.id.chipActive -> "active"
                R.id.chipCompleted -> "completed"
                else -> null
            }
            userId?.let {
                viewModel.loadPlans(it, currentStatus)
            }
        }
        
        binding.fabCreatePlan.setOnClickListener {
            // Navigate to create plan activity
            val intent = Intent(this, CreatePlanActivity::class.java)
            startActivity(intent)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
