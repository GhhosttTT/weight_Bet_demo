package com.weightloss.betting.ui.profile

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.os.Build
import android.provider.Settings
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.FragmentProfileBinding
import com.weightloss.betting.util.GenderMapper
import com.weightloss.betting.util.NotificationPermissionHelper
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class ProfileFragment : Fragment() {
    
    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!
    private val viewModel: ProfileViewModel by viewModels()
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private var userId: String? = null
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupObservers()
        setupListeners()
        loadUserProfile()
    }
    
    private fun loadUserProfile() {
        lifecycleScope.launch {
            userId = tokenManager.getUserId()
            android.util.Log.d("ProfileFragment", "User ID loaded: ${!userId.isNullOrBlank()}")
            if (userId != null) {
                viewModel.loadUserProfile(userId!!)
            } else {
                Toast.makeText(requireContext(), "用户未登录", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun setupObservers() {
        viewModel.profileState.observe(viewLifecycleOwner) { state ->
            android.util.Log.d("ProfileFragment", "Profile state changed: $state")
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
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
        viewModel.accountDeletionState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is AccountDeletionState.Loading -> binding.btnDeleteAccount.isEnabled = false
                is AccountDeletionState.Success -> {
                    lifecycleScope.launch {
                        viewModel.logout()
                        Toast.makeText(requireContext(), "账户已删除", Toast.LENGTH_SHORT).show()
                        goToLogin()
                    }
                }
                is AccountDeletionState.Error -> {
                    binding.btnDeleteAccount.isEnabled = true
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
                is AccountDeletionState.Idle -> Unit
            }
        }
    }
    
    private fun setupListeners() {
        binding.btnEdit.setOnClickListener {
            val intent = Intent(requireContext(), EditProfileActivity::class.java)
            startActivity(intent)
        }

        binding.btnNotificationSettings.setOnClickListener {
            openNotificationSettings()
        }
        
        binding.btnLogout.setOnClickListener {
            lifecycleScope.launch {
                viewModel.logout()
                Toast.makeText(requireContext(), "已退出登录", Toast.LENGTH_SHORT).show()
                val intent = Intent(requireContext(), com.weightloss.betting.ui.auth.LoginActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(intent)
                requireActivity().finish()
            }
        }
        binding.btnDeleteAccount.setOnClickListener { confirmDeleteAccount() }
    }

    private fun confirmDeleteAccount() {
        androidx.appcompat.app.AlertDialog.Builder(requireContext())
            .setTitle("删除账户")
            .setMessage("账户删除后将清理个人资料和本地照片，且无法恢复。进行中的计划或冻结资金需要先处理。确定继续吗？")
            .setNegativeButton("取消", null)
            .setPositiveButton("删除") { _, _ ->
                userId?.let { viewModel.deleteAccount(it) }
            }
            .show()
    }

    private fun openNotificationSettings() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(
                requireContext(),
                Manifest.permission.POST_NOTIFICATIONS
            ) != PackageManager.PERMISSION_GRANTED
        ) {
            requestPermissions(
                arrayOf(Manifest.permission.POST_NOTIFICATIONS),
                NotificationPermissionHelper.NOTIFICATION_PERMISSION_REQUEST_CODE
            )
            return
        }

        val settingsIntent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
            putExtra(Settings.EXTRA_APP_PACKAGE, requireContext().packageName)
        }
        startActivity(settingsIntent)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode != NotificationPermissionHelper.NOTIFICATION_PERMISSION_REQUEST_CODE) return

        if (grantResults.firstOrNull() == PackageManager.PERMISSION_GRANTED) {
            Toast.makeText(requireContext(), "通知权限已开启", Toast.LENGTH_SHORT).show()
        } else {
            Toast.makeText(requireContext(), "通知权限未开启，可在系统设置中修改", Toast.LENGTH_LONG).show()
            val settingsIntent = Intent(Settings.ACTION_APP_NOTIFICATION_SETTINGS).apply {
                putExtra(Settings.EXTRA_APP_PACKAGE, requireContext().packageName)
            }
            startActivity(settingsIntent)
        }
    }

    private fun goToLogin() {
        val intent = Intent(requireContext(), com.weightloss.betting.ui.auth.LoginActivity::class.java)
        intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
        startActivity(intent)
        requireActivity().finish()
    }
    
    private fun displayUserInfo(user: com.weightloss.betting.data.model.User) {
        android.util.Log.d("ProfileFragment", "Displaying profile info")
        binding.tvNickname.text = user.nickname
        binding.tvEmail.text = user.email
        binding.tvGender.text = GenderMapper.toDisplay(user.gender)
        binding.tvAge.text = "${user.age} 岁"
        binding.tvHeight.text = "${user.height} cm"
        binding.tvCurrentWeight.text = "${user.currentWeight} kg"
        binding.tvTargetWeight.text = user.targetWeight?.let { "$it kg" } ?: "未设置"
        android.util.Log.d("ProfileFragment", "User info displayed successfully")
    }
    
    override fun onResume() {
        super.onResume()
        // 每次返回时刷新用户信息
        userId?.let { viewModel.loadUserProfile(it, forceRefresh = true) }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
