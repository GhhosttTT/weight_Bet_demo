package com.weightloss.betting.ui.plan

import android.app.DatePickerDialog
import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.weightloss.betting.databinding.ActivityCreatePlanBinding
import com.weightloss.betting.ui.payment.ChargeActivity
import dagger.hilt.android.AndroidEntryPoint
import java.text.SimpleDateFormat
import java.util.*

@AndroidEntryPoint
class CreatePlanActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityCreatePlanBinding
    private val viewModel: CreatePlanViewModel by viewModels()
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
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
        // Toolbar is already defined in layout, no need to set as support action bar
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
                    // 跳转到计划详情页面，用户可以在那里邀请好友
                    val intent = Intent(this, PlanDetailActivity::class.java)
                    intent.putExtra("PLAN_ID", state.plan.id)
                    intent.putExtra("SHOW_INVITE", true) // 标记需要显示邀请功能
                    startActivity(intent)
                    finish()
                }
                is CreatePlanState.PaymentRequired -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnCreate.isEnabled = true
                    // 调起充值界面
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
        binding.etStartDate.setOnClickListener {
            showDatePicker { date ->
                startDate = date
                binding.etStartDate.setText(dateFormat.format(date))
            }
        }
        
        binding.etEndDate.setOnClickListener {
            showDatePicker { date ->
                endDate = date
                binding.etEndDate.setText(dateFormat.format(date))
            }
        }
        
        binding.btnCreate.setOnClickListener {
            createPlan()
        }
    }
    
    private fun showDatePicker(onDateSelected: (Date) -> Unit) {
        val calendar = Calendar.getInstance()
        val year = calendar.get(Calendar.YEAR)
        val month = calendar.get(Calendar.MONTH)
        val day = calendar.get(Calendar.DAY_OF_MONTH)
        
        DatePickerDialog(this, { _, selectedYear, selectedMonth, selectedDay ->
            calendar.set(selectedYear, selectedMonth, selectedDay)
            onDateSelected(calendar.time)
        }, year, month, day).show()
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
        
        if (startDate == null) {
            Toast.makeText(this, "请选择开始日期", Toast.LENGTH_SHORT).show()
            return
        }
        
        if (endDate == null) {
            Toast.makeText(this, "请选择结束日期", Toast.LENGTH_SHORT).show()
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
