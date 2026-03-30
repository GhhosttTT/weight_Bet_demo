package com.weightloss.betting.ui.social

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.google.android.material.tabs.TabLayout
import com.weightloss.betting.databinding.ActivityLeaderboardBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class LeaderboardActivity : BaseActivity() {
    
    private lateinit var binding: ActivityLeaderboardBinding
    private val viewModel: LeaderboardViewModel by viewModels()
    private lateinit var adapter: LeaderboardAdapter
    
    private var currentType = "weight-loss"
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityLeaderboardBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupRecyclerView()
        setupObservers()
        setupListeners()
        
        // 加载默认排行榜
        viewModel.loadLeaderboard(currentType)
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener {
            finish()
        }
    }
    
    private fun setupRecyclerView() {
        adapter = LeaderboardAdapter(currentType)
        binding.recyclerViewLeaderboard.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewLeaderboard.adapter = adapter
    }
    
    private fun setupObservers() {
        viewModel.leaderboardState.observe(this) { state ->
            when (state) {
                is LeaderboardState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.swipeRefresh.isRefreshing = false
                }
                is LeaderboardState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.swipeRefresh.isRefreshing = false
                    adapter.submitList(state.entries)
                }
                is LeaderboardState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.swipeRefresh.isRefreshing = false
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadLeaderboard(currentType)
        }
        
        binding.tabLayout.addOnTabSelectedListener(object : TabLayout.OnTabSelectedListener {
            override fun onTabSelected(tab: TabLayout.Tab?) {
                currentType = when (tab?.position) {
                    0 -> "weight-loss"
                    1 -> "check-in-streak"
                    2 -> "win-rate"
                    else -> "weight-loss"
                }
                
                // 更新适配器类型并重新加载数据
                adapter = LeaderboardAdapter(currentType)
                binding.recyclerViewLeaderboard.adapter = adapter
                viewModel.loadLeaderboard(currentType)
            }
            
            override fun onTabUnselected(tab: TabLayout.Tab?) {}
            override fun onTabReselected(tab: TabLayout.Tab?) {}
        })
    }
}
