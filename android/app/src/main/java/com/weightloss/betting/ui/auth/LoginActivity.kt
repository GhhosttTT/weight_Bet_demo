package com.weightloss.betting.ui.auth

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.credentials.CredentialManager
import androidx.credentials.CustomCredential
import androidx.credentials.GetCredentialRequest
import androidx.activity.viewModels
import androidx.lifecycle.lifecycleScope
import com.google.android.libraries.identity.googleid.GetGoogleIdOption
import com.google.android.libraries.identity.googleid.GoogleIdTokenCredential
import com.google.android.libraries.identity.googleid.GoogleIdTokenParsingException
import com.weightloss.betting.databinding.ActivityLoginBinding
import com.weightloss.betting.ui.MainActivity
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint
import java.util.UUID
import kotlinx.coroutines.launch

/**
 * 登录界面
 */
@AndroidEntryPoint
class LoginActivity : BaseActivity() {
    
    private lateinit var binding: ActivityLoginBinding
    private val viewModel: LoginViewModel by viewModels()
    private var googleSignInConfigured = false

    private val credentialManager by lazy { CredentialManager.create(this) }
    
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
        googleSignInConfigured = configuredGoogleClientId() != null
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
        val webClientId = configuredGoogleClientId()
        if (webClientId == null) {
            Toast.makeText(this, "Google 登录尚未配置，请联系管理员", Toast.LENGTH_LONG).show()
            return
        }
        val nonce = UUID.randomUUID().toString()
        val googleIdOption = GetGoogleIdOption.Builder()
            .setFilterByAuthorizedAccounts(false)
            .setServerClientId(webClientId)
            .setAutoSelectEnabled(false)
            .setNonce(nonce)
            .build()
        val request = GetCredentialRequest.Builder()
            .addCredentialOption(googleIdOption)
            .build()
        showLoading(true)
        lifecycleScope.launch {
            try {
                val result = credentialManager.getCredential(this@LoginActivity, request)
                val credential = result.credential
                if (credential is CustomCredential &&
                    credential.type == GoogleIdTokenCredential.TYPE_GOOGLE_ID_TOKEN_CREDENTIAL
                ) {
                    val googleCredential = GoogleIdTokenCredential.createFrom(credential.data)
                    viewModel.googleLogin(googleCredential.idToken, nonce)
                } else {
                    showLoading(false)
                    Toast.makeText(this@LoginActivity, "Google 未返回有效身份凭证", Toast.LENGTH_LONG).show()
                }
            } catch (error: GoogleIdTokenParsingException) {
                showLoading(false)
                Log.e("LoginActivity", "Google credential parsing failed", error)
                Toast.makeText(this@LoginActivity, "Google 登录凭证无效，请重试", Toast.LENGTH_LONG).show()
            } catch (error: Exception) {
                showLoading(false)
                Log.e("LoginActivity", "Google sign-in failed", error)
                Toast.makeText(this@LoginActivity, "Google 登录失败，请重试", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun configuredGoogleClientId(): String? {
        val value = getString(com.weightloss.betting.R.string.default_web_client_id).trim()
        if (value.isEmpty() || value.startsWith("\$")) return null
        if (value.startsWith("YOUR_") || value.equals("replace_me", ignoreCase = true)) return null
        return value.takeIf { it.matches(Regex("^[0-9]+-[a-z0-9-]+\\.apps\\.googleusercontent\\.com$")) }
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
