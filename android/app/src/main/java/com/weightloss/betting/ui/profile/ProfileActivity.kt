package com.weightloss.betting.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.ActivityProfileBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class ProfileActivity : BaseActivity() {
    
    private lateinit var binding: ActivityProfileBinding
    private val viewModel: ProfileViewModel by viewModels()
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private var userId: String? = null
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupObservers()
        setupListeners()
        
        // Load user ID and profile
        lifecycleScope.launch {
            userId = tokenManager.getUserId()
            android.util.Log.d("ProfileActivity", "User ID loaded: ${!userId.isNullOrBlank()}")
            if (userId != null) {
                viewModel.loadUserProfile(userId!!)
            } else {
                Toast.makeText(this@ProfileActivity, "用户未登录", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
    
    private fun setupObservers() {
        viewModel.profileState.observe(this) { state ->
            android.util.Log.d("ProfileActivity", "Profile state changed: $state")
            when (state) {
                is ProfileState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnEdit.isEnabled = false
                }
                is ProfileState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnEdit.isEnabled = true
                    displayUserInfo(state.user)
                }
                is ProfileState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnEdit.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        viewModel.accountDeletionState.observe(this) { state ->
            when (state) {
                is AccountDeletionState.Loading -> binding.btnDeleteAccount.isEnabled = false
                is AccountDeletionState.Success -> {
                    lifecycleScope.launch {
                        viewModel.logout()
                        Toast.makeText(this@ProfileActivity, "账户已删除", Toast.LENGTH_SHORT).show()
                        goToLogin()
                    }
                }
                is AccountDeletionState.Error -> {
                    binding.btnDeleteAccount.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
                is AccountDeletionState.Idle -> Unit
            }
        }
    }
    
    private fun setupListeners() {
        binding.btnEdit.setOnClickListener {
            // Navigate to edit profile activity
            val intent = Intent(this, EditProfileActivity::class.java)
            startActivity(intent)
        }
        
        // 退出登录功能
        binding.btnLogout.setOnClickListener {
            lifecycleScope.launch {
                viewModel.logout()
                Toast.makeText(this@ProfileActivity, "已退出登录", Toast.LENGTH_SHORT).show()
                goToLogin()
            }
        }
        binding.btnDeleteAccount.setOnClickListener { confirmDeleteAccount() }
    }

    private fun confirmDeleteAccount() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("删除账户")
            .setMessage("账户删除后将清理个人资料和本地照片，且无法恢复。进行中的计划或冻结资金需要先处理。确定继续吗？")
            .setNegativeButton("取消", null)
            .setPositiveButton("删除") { _, _ ->
                userId?.let { viewModel.deleteAccount(it) }
            }
            .show()
    }

    private fun goToLogin() {
        val intent = Intent(this, com.weightloss.betting.ui.auth.LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        finish()
    }
    
    private fun displayUserInfo(user: com.weightloss.betting.data.model.User) {
        android.util.Log.d("ProfileActivity", "Displaying profile info")
        binding.tvNickname.text = user.nickname
        binding.tvGender.text = when (user.gender) {
            "male" -> "男"
            "female" -> "女"
            else -> "其他"
        }
        binding.tvAge.text = "${user.age} 岁"
        binding.tvHeight.text = "${user.height} cm"
        binding.tvCurrentWeight.text = "${user.currentWeight} kg"
        binding.tvTargetWeight.text = user.targetWeight?.let { "$it kg" } ?: "未设置"
        android.util.Log.d("ProfileActivity", "User info displayed successfully")
    }
}
