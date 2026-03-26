package com.weightloss.betting.ui.auth

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.weightloss.betting.R
import com.weightloss.betting.databinding.ActivityRegisterBinding
import com.weightloss.betting.ui.MainActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * 注册界面
 */
@AndroidEntryPoint
class RegisterActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityRegisterBinding
    private val viewModel: RegisterViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityRegisterBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViews()
        observeViewModel()
    }
    
    private fun setupViews() {
        // 设置性别下拉框
        val genders = arrayOf("male", "female", "other")
        val genderAdapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, genders)
        genderAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerGender.adapter = genderAdapter
        
        // 注册按钮
        binding.btnRegister.setOnClickListener {
            val email = binding.etEmail.text.toString()
            val password = binding.etPassword.text.toString()
            val confirmPassword = binding.etConfirmPassword.text.toString()
            val nickname = binding.etNickname.text.toString()
            val gender = binding.spinnerGender.selectedItem.toString()
            val age = binding.etAge.text.toString().toIntOrNull() ?: 0
            val height = binding.etHeight.text.toString().toDoubleOrNull() ?: 0.0
            val currentWeight = binding.etCurrentWeight.text.toString().toDoubleOrNull() ?: 0.0
            
            viewModel.register(
                email, password, confirmPassword, nickname, gender, age, height, currentWeight
            )
        }
        
        // 返回登录
        binding.tvLogin.setOnClickListener {
            finish()
        }
    }
    
    private fun observeViewModel() {
        // 观察注册状态
        viewModel.registerState.observe(this) { state ->
            when (state) {
                is RegisterState.Loading -> {
                    showLoading(true)
                }
                is RegisterState.Success -> {
                    showLoading(false)
                    Toast.makeText(this, "注册成功", Toast.LENGTH_SHORT).show()
                    navigateToMain()
                }
                is RegisterState.Error -> {
                    showLoading(false)
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        binding.progressBar.visibility = if (show) View.VISIBLE else View.GONE
        binding.btnRegister.isEnabled = !show
    }
    
    private fun navigateToMain() {
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}
