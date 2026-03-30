package com.weightloss.betting.ui.plan

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.google.android.material.datepicker.CalendarConstraints
import com.google.android.material.datepicker.DateValidatorPointForward
import com.google.android.material.datepicker.MaterialDatePicker
import com.weightloss.betting.databinding.ActivityCreatePlanBinding
import com.weightloss.betting.ui.base.BaseActivity
import com.weightloss.betting.ui.payment.ChargeActivity
import dagger.hilt.android.AndroidEntryPoint
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class CreatePlanActivity : BaseActivity() {
    
    private lateinit var binding: ActivityCreatePlanBinding
    private val viewModel: CreatePlanViewModel by viewModels()
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private val displayDateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
    private var startDate: Date? = null
    private var endDate: Date? = null
    
    companion object {
        private const val REQUEST_CODE_CHARGE = 1001
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCreatePlanBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupToolbar()
        setupObservers()
        setupListeners()
    }
    
    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener {
            finish()
        }
    }
    
    private fun setupObservers() {
        viewModel.createPlanState.observe(this) { state ->
            when (state) {
                is CreatePlanState.Idle -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnCreate.isEnabled = true
                }
                is CreatePlanState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnCreate.isEnabled = false
                }
                is CreatePlanState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, "计划创建成功", Toast.LENGTH_SHORT).show()
                    val intent = Intent(this, PlanDetailActivity::class.java)
                    intent.putExtra("PLAN_ID", state.plan.id)
                    intent.putExtra("SHOW_INVITE", true)
                    startActivity(intent)
                    finish()
                }
                is CreatePlanState.PaymentRequired -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnCreate.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                    val intent = Intent(this, ChargeActivity::class.java)
                    intent.putExtra("required_amount", state.requiredAmount)
                    startActivityForResult(intent, REQUEST_CODE_CHARGE)
                }
                is CreatePlanState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnCreate.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.etDateRange.setOnClickListener {
            showDateRangePicker()
        }
        
        binding.btnCreate.setOnClickListener {
            createPlan()
        }
    }
    
    private fun showDateRangePicker() {
        val today = MaterialDatePicker.todayInUtcMilliseconds()
        
        val constraintsBuilder = CalendarConstraints.Builder()
            .setValidator(DateValidatorPointForward.now())
        
        val datePicker = MaterialDatePicker.Builder.dateRangePicker()
            .setTitleText("选择计划日期")
            .setCalendarConstraints(constraintsBuilder.build())
            .build()
        
        datePicker.addOnPositiveButtonClickListener { selection ->
            val startMillis = selection.first
            val endMillis = selection.second
            
            val startCalendar = Calendar.getInstance(TimeZone.getTimeZone("UTC"))
            startCalendar.timeInMillis = startMillis
            
            val endCalendar = Calendar.getInstance(TimeZone.getTimeZone("UTC"))
            endCalendar.timeInMillis = endMillis
            
            startDate = startCalendar.time
            endDate = endCalendar.time
            
            val startStr = displayDateFormat.format(startDate)
            val endStr = displayDateFormat.format(endDate)
            binding.etDateRange.setText("$startStr 至 $endStr")
        }
        
        datePicker.show(supportFragmentManager, "DATE_RANGE_PICKER")
    }
    
    private fun createPlan() {
        val betAmount = binding.etBetAmount.text.toString()
        val initialWeight = binding.etInitialWeight.text.toString()
        val targetWeight = binding.etTargetWeight.text.toString()
        val description = binding.etDescription.text.toString().takeIf { it.isNotBlank() }
        
        if (betAmount.isBlank()) {
            Toast.makeText(this, "请输入赌金金额", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (startDate == null || endDate == null) {
            Toast.makeText(this, "请选择计划日期范围", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (initialWeight.isBlank()) {
            Toast.makeText(this, "请输入初始体重", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (targetWeight.isBlank()) {
            Toast.makeText(this, "请输入目标体重", Toast.LENGTH_SHORT).show()
            return
        }
        
        viewModel.createPlan(
            betAmount = betAmount,
            startDate = startDate!!,
            endDate = endDate!!,
            initialWeight = initialWeight,
            targetWeight = targetWeight,
            description = description
        )
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
    
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == REQUEST_CODE_CHARGE && resultCode == RESULT_OK) {
            // 充值成功后自动重试创建计划
            Toast.makeText(this, "充值成功,正在重新创建计划...", Toast.LENGTH_SHORT).show()
            createPlan()
        }
    }
}
