package com.weightloss.betting.ui.profile

import android.os.Bundle
import android.view.View
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.activity.viewModels
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.R
import com.weightloss.betting.databinding.ActivityEditProfileBinding
import com.weightloss.betting.ui.base.BaseActivity
import com.weightloss.betting.util.GenderMapper
import com.weightloss.betting.data.remote.TokenManager
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject
import kotlinx.coroutines.launch

@AndroidEntryPoint
class EditProfileActivity : BaseActivity() {
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private lateinit var binding: ActivityEditProfileBinding
    private val viewModel: EditProfileViewModel by viewModels()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityEditProfileBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupGenderSpinner()
        setupObservers()
        setupListeners()
        
        // 设置返回按钮
        binding.btnBack.setOnClickListener {
            finish()
        }
        
        // Load current user data
        lifecycleScope.launch {
            val userId = tokenManager.getUserId()
            if (userId != null) {
                viewModel.loadUserProfile(userId)
            } else {
                Toast.makeText(this@EditProfileActivity, "请先登录", Toast.LENGTH_SHORT).show()
                finish()
            }
        }
    }
    
    private fun setupGenderSpinner() {
        val adapter = ArrayAdapter(this, android.R.layout.simple_spinner_item, GenderMapper.displayOptions)
        adapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item)
        binding.spinnerGender.adapter = adapter
    }
    
    private fun setupObservers() {
        viewModel.currentUser.observe(this) { user ->
            user?.let {
                // Populate fields with current user data
                binding.etNickname.setText(it.nickname)
                binding.spinnerGender.setSelection(GenderMapper.getPosition(it.gender))
                binding.etAge.setText(it.age.toString())
                binding.etHeight.setText(it.height.toString())
                binding.etCurrentWeight.setText(it.currentWeight.toString())
                it.targetWeight?.let { tw ->
                    binding.etTargetWeight.setText(tw.toString())
                }
            }
        }
        
        viewModel.editProfileState.observe(this) { state ->
            when (state) {
                is EditProfileState.Idle -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSave.isEnabled = true
                }
                is EditProfileState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnSave.isEnabled = false
                }
                is EditProfileState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSave.isEnabled = true
                    Toast.makeText(this, "更新成功", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is EditProfileState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSave.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.btnSave.setOnClickListener {
            lifecycleScope.launch {
                val userId = tokenManager.getUserId()
                if (userId == null) {
                    Toast.makeText(this@EditProfileActivity, "请先登录", Toast.LENGTH_SHORT).show()
                    return@launch
                }
                
                val nickname = binding.etNickname.text.toString()
                val genderDisplay = binding.spinnerGender.selectedItem.toString()
                val gender = GenderMapper.toValue(genderDisplay)
                val age = binding.etAge.text.toString()
                val height = binding.etHeight.text.toString()
                val currentWeight = binding.etCurrentWeight.text.toString()
                val targetWeight = binding.etTargetWeight.text.toString()
                
                viewModel.updateProfile(
                    userId = userId,
                    nickname = nickname,
                    gender = gender,
                    age = age,
                    height = height,
                    currentWeight = currentWeight,
                    targetWeight = targetWeight.ifBlank { null }
                )
            }
        }
    }
}
