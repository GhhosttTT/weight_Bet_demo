package com.weightloss.betting.ui.auth

import android.content.Intent
import android.os.Bundle
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.ui.MainActivity
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 启动页 - 检查用户登录状态
 */
@AndroidEntryPoint
class SplashActivity : BaseActivity() {
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 检查登录状态
        checkLoginStatus()
    }
    
    private fun checkLoginStatus() {
        lifecycleScope.launch {
            val accessToken = tokenManager.getAccessToken()
            
            if (accessToken != null) {
                // 已登录,跳转到主页
                navigateToMain()
            } else {
                // 未登录,跳转到登录页
                navigateToLogin()
            }
        }
    }
    
    private fun navigateToMain() {
        val intent = Intent(this, MainActivity::class.java)
        startActivity(intent)
        finish()
    }
    
    private fun navigateToLogin() {
        val intent = Intent(this, LoginActivity::class.java)
        startActivity(intent)
        finish()
    }
}
