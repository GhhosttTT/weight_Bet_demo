package com.weightloss.betting.ui.social

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.GridLayoutManager
import com.weightloss.betting.databinding.ActivityBadgesBinding
import com.weightloss.betting.ui.base.BaseActivity
import com.weightloss.betting.data.remote.TokenManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject
import kotlinx.coroutines.launch

@AndroidEntryPoint
class BadgesActivity : BaseActivity() {
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private lateinit var binding: ActivityBadgesBinding
    private val viewModel: BadgesViewModel by viewModels()
    private lateinit var adapter: BadgesAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityBadgesBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupRecyclerView()
        setupObservers()
        
        // 加载勋章
        lifecycleScope.launch {
            val userId = tokenManager.getUserId()
            if (userId != null) {
                viewModel.loadBadges(userId)
            } else {
                Toast.makeText(this@BadgesActivity, "请先登录", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener {
            finish()
        }
    }
    
    private fun setupRecyclerView() {
        adapter = BadgesAdapter()
        binding.recyclerViewBadges.layoutManager = GridLayoutManager(this, 1)
        binding.recyclerViewBadges.adapter = adapter
    }
    
    private fun setupObservers() {
        viewModel.badgesState.observe(this) { state ->
            when (state) {
                is BadgesState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.tvEmptyState.visibility = View.GONE
                }
                is BadgesState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    if (state.badges.isEmpty()) {
                        binding.tvEmptyState.visibility = View.VISIBLE
                        binding.recyclerViewBadges.visibility = View.GONE
                    } else {
                        binding.tvEmptyState.visibility = View.GONE
                        binding.recyclerViewBadges.visibility = View.VISIBLE
                        adapter.submitList(state.badges)
                    }
                }
                is BadgesState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
