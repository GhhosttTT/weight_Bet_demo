package com.weightloss.betting.ui.payment

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.weightloss.betting.R
import com.weightloss.betting.databinding.ActivityChargeBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class ChargeActivity : BaseActivity() {
    
    private lateinit var binding: ActivityChargeBinding
    private val viewModel: ChargeViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityChargeBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupObservers()
        setupListeners()
        
        // 获取需要充值的金额
        val requiredAmount = intent.getDoubleExtra("required_amount", 0.0)
        if (requiredAmount > 0) {
            binding.etAmount.setText(requiredAmount.toString())
            // 如果金额匹配快捷选项,自动选中对应的Chip
            when (requiredAmount.toInt()) {
                50 -> binding.chipGroupAmount.check(R.id.chip50)
                100 -> binding.chipGroupAmount.check(R.id.chip100)
                200 -> binding.chipGroupAmount.check(R.id.chip200)
                500 -> binding.chipGroupAmount.check(R.id.chip500)
            }
        }
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupObservers() {
        viewModel.chargeState.observe(this) { state ->
            when (state) {
                is ChargeState.Idle -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnCharge.isEnabled = true
                }
                is ChargeState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnCharge.isEnabled = false
                }
                is ChargeState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, "充值成功", Toast.LENGTH_SHORT).show()
                    setResult(RESULT_OK)
                    finish()
                }
                is ChargeState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnCharge.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.chipGroupAmount.setOnCheckedChangeListener { _, checkedId ->
            val amount = when (checkedId) {
                R.id.chip50 -> "50"
                R.id.chip100 -> "100"
                R.id.chip200 -> "200"
                R.id.chip500 -> "500"
                else -> null
            }
            amount?.let {
                binding.etAmount.setText(it)
            }
        }
        
        binding.btnCharge.setOnClickListener {
            val amount = binding.etAmount.text.toString()
            
            if (amount.isBlank()) {
                Toast.makeText(this, "请输入充值金额", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            viewModel.createCharge(amount)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
