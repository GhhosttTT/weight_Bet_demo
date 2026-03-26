package com.weightloss.betting.ui.social

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.GridLayoutManager
import com.weightloss.betting.databinding.ActivityBadgesBinding
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class BadgesActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityBadgesBinding
    private val viewModel: BadgesViewModel by viewModels()
    private lateinit var adapter: BadgesAdapter
    
    // TODO: Get actual user ID from session/preferences
    private val userId = "current_user_id"
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityBadgesBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupRecyclerView()
        setupObservers()
        
        // 加载勋章
        viewModel.loadBadges(userId)
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
