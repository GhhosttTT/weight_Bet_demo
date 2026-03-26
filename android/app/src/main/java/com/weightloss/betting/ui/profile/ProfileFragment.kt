package com.weightloss.betting.ui.profile

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.FragmentProfileBinding
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
            android.util.Log.d("ProfileFragment", "User ID from TokenManager: $userId")
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
    }
    
    private fun setupListeners() {
        binding.btnEdit.setOnClickListener {
            val intent = Intent(requireContext(), EditProfileActivity::class.java)
            startActivity(intent)
        }
        
        binding.btnLogout.setOnClickListener {
            lifecycleScope.launch {
                tokenManager.clearTokens()
                Toast.makeText(requireContext(), "已退出登录", Toast.LENGTH_SHORT).show()
                val intent = Intent(requireContext(), com.weightloss.betting.ui.auth.LoginActivity::class.java)
                intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
                startActivity(intent)
                requireActivity().finish()
            }
        }
    }
    
    private fun displayUserInfo(user: com.weightloss.betting.data.model.User) {
        android.util.Log.d("ProfileFragment", "Displaying user info: $user")
        binding.tvNickname.text = user.nickname
        binding.tvEmail.text = user.email
        binding.tvGender.text = when (user.gender) {
            "male" -> "男"
            "female" -> "女"
            else -> "其他"
        }
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
