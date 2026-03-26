package com.weightloss.betting.ui.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import com.weightloss.betting.databinding.ActivityLoginBinding
import com.weightloss.betting.ui.MainActivity
import dagger.hilt.android.AndroidEntryPoint

/**
 * 登录界面
 */
@AndroidEntryPoint
class LoginActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    private val viewModel: LoginViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("LoginActivity", "onCreate called")
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        Log.d("LoginActivity", "Layout inflated and content view set")
        
        setupViews()
        observeViewModel()
        Log.d("LoginActivity", "Setup completed")
    }
    
    private fun setupViews() {
        Log.d("LoginActivity", "setupViews called")
        // 登录按钮
        binding.btnLogin.setOnClickListener {
            val email = binding.etEmail.text.toString()
            val password = binding.etPassword.text.toString()
            Log.d("LoginActivity", "Login button clicked, email: $email")
            viewModel.login(email, password)
        }
        
        // 注册按钮
        binding.tvRegister.setOnClickListener {
            Log.d("LoginActivity", "Register button clicked")
            startActivity(Intent(this, RegisterActivity::class.java))
        }
        
        // Google 登录按钮
        binding.btnGoogleLogin.setOnClickListener {
            Log.d("LoginActivity", "Google login button clicked")
            // TODO: 集成 Google Sign-In SDK
            Toast.makeText(this, "Google 登录功能开发中", Toast.LENGTH_SHORT).show()
        }
    }
    
    private fun observeViewModel() {
        // 观察登录状态
        viewModel.loginState.observe(this) { state ->
            when (state) {
                is LoginState.Loading -> {
                    showLoading(true)
                }
                is LoginState.Success -> {
                    showLoading(false)
                    Toast.makeText(this, "登录成功", Toast.LENGTH_SHORT).show()
                    navigateToMain()
                }
                is LoginState.Error -> {
                    showLoading(false)
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun showLoading(show: Boolean) {
        binding.progressBar.visibility = if (show) View.VISIBLE else View.GONE
        binding.btnLogin.isEnabled = !show
        binding.btnGoogleLogin.isEnabled = !show
    }
    
    private fun navigateToMain() {
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}
