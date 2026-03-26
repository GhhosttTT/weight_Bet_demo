package com.weightloss.betting.ui.payment

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.ActivityBalanceBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class BalanceActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityBalanceBinding
    private val viewModel: BalanceViewModel by viewModels()
    private lateinit var adapter: TransactionAdapter
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private var userId: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityBalanceBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupRecyclerView()
        setupObservers()
        setupListeners()
        
        // Load user ID and data
        lifecycleScope.launch {
            userId = tokenManager.getUserId()
            if (userId != null) {
                viewModel.loadBalance(userId!!)
                viewModel.loadTransactions(userId!!)
            } else {
                Toast.makeText(this@BalanceActivity, "用户未登录", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupRecyclerView() {
        adapter = TransactionAdapter()
        binding.recyclerViewTransactions.layoutManager = LinearLayoutManager(this)
        binding.recyclerViewTransactions.adapter = adapter
    }
    
    private fun setupObservers() {
        viewModel.balanceState.observe(this) { state ->
            when (state) {
                is BalanceState.Loading -> {
                    // Handled by SwipeRefreshLayout
                }
                is BalanceState.Success -> {
                    binding.swipeRefresh.isRefreshing = false
                    binding.tvAvailableBalance.text = "¥${String.format("%.2f", state.balance.availableBalance)}"
                    binding.tvFrozenBalance.text = "¥${String.format("%.2f", state.balance.frozenBalance)}"
                }
                is BalanceState.Error -> {
                    binding.swipeRefresh.isRefreshing = false
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        
        viewModel.transactionListState.observe(this) { state ->
            when (state) {
                is TransactionListState.Loading -> {
                    // Handled by SwipeRefreshLayout
                }
                is TransactionListState.Success -> {
                    binding.swipeRefresh.isRefreshing = false
                    if (state.transactions.isEmpty()) {
                        binding.tvEmptyTransactions.visibility = View.VISIBLE
                        binding.recyclerViewTransactions.visibility = View.GONE
                    } else {
                        binding.tvEmptyTransactions.visibility = View.GONE
                        binding.recyclerViewTransactions.visibility = View.VISIBLE
                        adapter.submitList(state.transactions)
                    }
                }
                is TransactionListState.Error -> {
                    binding.swipeRefresh.isRefreshing = false
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.swipeRefresh.setOnRefreshListener {
            userId?.let {
                viewModel.loadBalance(it, forceRefresh = true)
                viewModel.loadTransactions(it, forceRefresh = true)
            }
        }
        
        binding.btnCharge.setOnClickListener {
            val intent = Intent(this, ChargeActivity::class.java)
            startActivity(intent)
        }
        
        binding.btnWithdraw.setOnClickListener {
            val intent = Intent(this, WithdrawActivity::class.java)
            startActivity(intent)
        }
    }
    
    override fun onResume() {
        super.onResume()
        // Refresh data when returning to this activity
        userId?.let {
            viewModel.loadBalance(it, forceRefresh = true)
            viewModel.loadTransactions(it, forceRefresh = true)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
