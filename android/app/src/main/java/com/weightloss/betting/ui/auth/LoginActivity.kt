package com.weightloss.betting.ui.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.activity.result.contract.ActivityResultContracts
import com.weightloss.betting.databinding.ActivityLoginBinding
import com.weightloss.betting.ui.MainActivity
import com.weightloss.betting.ui.base.BaseActivity
import com.google.android.gms.auth.api.signin.GoogleSignIn
import com.google.android.gms.auth.api.signin.GoogleSignInOptions
import dagger.hilt.android.AndroidEntryPoint

/**
 * 登录界面
 */
@AndroidEntryPoint
class LoginActivity : BaseActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    private val viewModel: LoginViewModel by viewModels()
    private var googleSignInConfigured = false

    private val googleSignInLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode != RESULT_OK) {
            showLoading(false)
            return@registerForActivityResult
        }
        val task = GoogleSignIn.getSignedInAccountFromIntent(result.data)
        try {
            val idToken = task.result?.idToken
            if (idToken.isNullOrBlank()) {
                showLoading(false)
                Toast.makeText(this, "Google 未返回有效身份凭证", Toast.LENGTH_LONG).show()
            } else {
                viewModel.googleLogin(idToken)
            }
        } catch (error: Exception) {
            showLoading(false)
            Log.e("LoginActivity", "Google sign-in failed", error)
            Toast.makeText(this, "Google 登录失败，请重试", Toast.LENGTH_LONG).show()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("LoginActivity", "onCreate called")
        binding = ActivityLoginBinding.inflate(layoutInflater)
        setContentView(binding.root)
        Log.d("LoginActivity", "Layout inflated and content view set")
        
        setupViews()
        updateGoogleSignInAvailability()
        observeViewModel()
        Log.d("LoginActivity", "Setup completed")
    }

    private fun updateGoogleSignInAvailability() {
        googleSignInConfigured = !getString(com.weightloss.betting.R.string.default_web_client_id)
            .startsWith("YOUR_")
        binding.btnGoogleLogin.isEnabled = googleSignInConfigured
        binding.btnGoogleLogin.alpha = if (googleSignInConfigured) 1f else 0.55f
        if (!googleSignInConfigured) {
            binding.btnGoogleLogin.text = "Google 登录未配置"
            binding.btnGoogleLogin.contentDescription = "请先配置 Google OAuth Client ID"
        }
    }
    
    private fun setupViews() {
        Log.d("LoginActivity", "setupViews called")
        // 登录按钮
        binding.btnLogin.setOnClickListener {
            val email = binding.etEmail.text.toString()
            val password = binding.etPassword.text.toString()
            Log.d("LoginActivity", "Login button clicked")
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
            startGoogleSignIn()
        }
    }

    private fun startGoogleSignIn() {
        val webClientId = getString(com.weightloss.betting.R.string.default_web_client_id)
        if (webClientId.startsWith("YOUR_")) {
            Toast.makeText(this, "Google 登录尚未配置，请联系管理员", Toast.LENGTH_LONG).show()
            return
        }
        val options = GoogleSignInOptions.Builder(GoogleSignInOptions.DEFAULT_SIGN_IN)
            .requestIdToken(webClientId)
            .requestEmail()
            .build()
        val client = GoogleSignIn.getClient(this, options)
        showLoading(true)
        googleSignInLauncher.launch(client.signInIntent)
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
        binding.btnGoogleLogin.isEnabled = !show && googleSignInConfigured
    }
    
    private fun navigateToMain() {
        val intent = Intent(this, MainActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
}
