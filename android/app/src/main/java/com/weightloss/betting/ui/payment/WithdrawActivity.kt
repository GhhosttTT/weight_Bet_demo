package com.weightloss.betting.ui.payment

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.weightloss.betting.databinding.ActivityWithdrawBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class WithdrawActivity : BaseActivity() {
    
    private lateinit var binding: ActivityWithdrawBinding
    private val viewModel: WithdrawViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityWithdrawBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupObservers()
        setupListeners()
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupObservers() {
        viewModel.withdrawState.observe(this) { state ->
            when (state) {
                is WithdrawState.Idle -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnWithdraw.isEnabled = true
                }
                is WithdrawState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnWithdraw.isEnabled = false
                }
                is WithdrawState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, "提现申请已提交,请等待审核", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is WithdrawState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnWithdraw.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.btnWithdraw.setOnClickListener {
            val amount = binding.etAmount.text.toString()
            
            if (amount.isBlank()) {
                Toast.makeText(this, "请输入提现金额", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            viewModel.createWithdraw(amount)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
