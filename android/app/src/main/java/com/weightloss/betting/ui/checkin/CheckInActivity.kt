package com.weightloss.betting.ui.checkin

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.weightloss.betting.databinding.ActivityCheckInBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CheckInActivity : BaseActivity() {
    
    private lateinit var binding: ActivityCheckInBinding
    private val viewModel: CheckInViewModel by viewModels()
    
    private var planId: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCheckInBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        planId = intent.getStringExtra("PLAN_ID")
        
        if (planId == null) {
            Toast.makeText(this, "计划ID无效", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        setupToolbar()
        setupObservers()
        setupListeners()
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupObservers() {
        viewModel.checkInState.observe(this) { state ->
            when (state) {
                is CheckInState.Idle -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSubmit.isEnabled = true
                }
                is CheckInState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnSubmit.isEnabled = false
                }
                is CheckInState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, "打卡成功", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is CheckInState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSubmit.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.btnSubmit.setOnClickListener {
            submitCheckIn()
        }
    }
    
    private fun submitCheckIn() {
        val weight = binding.etWeight.text.toString()
        val note = binding.etNote.text.toString().takeIf { it.isNotBlank() }
        
        if (weight.isBlank()) {
            Toast.makeText(this, "请输入体重", Toast.LENGTH_SHORT).show()
            return
        }
        
        viewModel.createCheckIn(planId!!, weight, note)
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
