package com.weightloss.betting.ui.plan

import android.app.Dialog
import android.content.Context
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.DialogFragment
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.lifecycleScope
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.weightloss.betting.R
import com.weightloss.betting.data.model.UserSearchResult
import com.weightloss.betting.databinding.DialogInviteFriendBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class InviteFriendDialog : DialogFragment() {
    
    private var _binding: DialogInviteFriendBinding? = null
    private val binding get() = _binding!!
    
    private lateinit var viewModel: InviteFriendViewModel
    private var planId: String? = null
    
    companion object {
        const val ARG_PLAN_ID = "plan_id"
        
        fun newInstance(planId: String): InviteFriendDialog {
            return InviteFriendDialog().apply {
                arguments = Bundle().apply {
                    putString(ARG_PLAN_ID, planId)
                }
            }
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        planId = arguments?.getString(ARG_PLAN_ID)
        
        if (planId == null) {
            Toast.makeText(requireContext(), "计划 ID 无效", Toast.LENGTH_SHORT).show()
            dismiss()
        }
        
        // Initialize ViewModel early
        viewModel = ViewModelProvider(requireActivity())[InviteFriendViewModel::class.java]
    }
    
    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        _binding = DialogInviteFriendBinding.inflate(LayoutInflater.from(requireContext()))
        
        android.util.Log.d("InviteFriendDialog", "Creating dialog")
        
        val dialog = MaterialAlertDialogBuilder(requireContext())
            .setView(binding.root)
            .create()
        
        // Set up dialog properties
        dialog.setCanceledOnTouchOutside(true)
        dialog.setCancelable(true)
        
        android.util.Log.d("InviteFriendDialog", "Dialog created")

        // 直接在 onCreateDialog 中设置观察者和监听器，确保在 DialogFragment 没有走 onCreateView/onViewCreated 时也能生效
        setupObservers()
        setupListeners()

        return dialog
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // 兼容性: 如果 onViewCreated 被调用，这里不再重复设置
    }

    private fun setupObservers() {
        lifecycleScope.launch {
            viewModel.searchState.collect { state ->
                when (state) {
                    is SearchState.Loading -> {
                        binding.progressBar.visibility = View.VISIBLE
                        binding.searchResultContainer.visibility = View.GONE
                    }
                    is SearchState.Success -> {
                        binding.progressBar.visibility = View.GONE
                        binding.searchResultContainer.visibility = View.VISIBLE
                        displaySearchResult(state.user)
                    }
                    is SearchState.Error -> {
                        binding.progressBar.visibility = View.GONE
                        binding.searchResultContainer.visibility = View.GONE
                        Toast.makeText(requireContext(), state.message, Toast.LENGTH_SHORT).show()
                    }
                    else -> {
                        binding.progressBar.visibility = View.GONE
                        binding.searchResultContainer.visibility = View.GONE
                    }
                }
            }
        }
        
        lifecycleScope.launch {
            viewModel.inviteState.collect { state ->
                when (state) {
                    is InviteState.Loading -> {
                        binding.btnConfirmInvite.isEnabled = false
                        binding.btnSearchFriend.isEnabled = false
                    }
                    is InviteState.Success -> {
                        Toast.makeText(requireContext(), "邀请发送成功", Toast.LENGTH_SHORT).show()
                        dismiss()
                    }
                    is InviteState.Error -> {
                        binding.btnConfirmInvite.isEnabled = true
                        binding.btnSearchFriend.isEnabled = true
                        Toast.makeText(requireContext(), state.message, Toast.LENGTH_SHORT).show()
                    }
                    else -> {
                        binding.btnConfirmInvite.isEnabled = true
                        binding.btnSearchFriend.isEnabled = true
                    }
                }
            }
        }
    }
    
    private fun displaySearchResult(user: UserSearchResult) {
        binding.tvFriendName.text = "姓名：${user.nickname}"
        binding.tvFriendAge.text = "年龄：${user.age}岁"
        binding.tvFriendGender.text = "性别：${when (user.gender.lowercase()) {
            "male" -> "男"
            "female" -> "女"
            else -> user.gender
        }}"
        
        // Enable confirm button after displaying result
        binding.btnConfirmInvite.isEnabled = true
    }
    
    private fun setupListeners() {
        android.util.Log.d("InviteFriendDialog", "Setting up listeners")
        android.util.Log.d("InviteFriendDialog", "btnSearchFriend: ${binding.btnSearchFriend}")
        android.util.Log.d("InviteFriendDialog", "btnCancel: ${binding.btnCancel}")
        
        binding.btnSearchFriend.setOnClickListener {
            android.util.Log.d("InviteFriendDialog", "Search button clicked")
            val email = binding.emailInput.text.toString().trim()
            android.util.Log.d("InviteFriendDialog", "Email: $email")
            
            if (email.isBlank()) {
                binding.emailInput.error = "请输入邮箱地址"
                android.util.Log.d("InviteFriendDialog", "Email is blank")
                return@setOnClickListener
            }
            
            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                binding.emailInput.error = "邮箱格式无效"
                android.util.Log.d("InviteFriendDialog", "Email format invalid")
                return@setOnClickListener
            }
            
            android.util.Log.d("InviteFriendDialog", "Calling viewModel.searchFriend")
            viewModel.searchFriend(email)
        }
        
        binding.btnCancel.setOnClickListener {
            android.util.Log.d("InviteFriendDialog", "Cancel button clicked")
            dismiss()
        }
        
        binding.btnConfirmInvite.setOnClickListener {
            android.util.Log.d("InviteFriendDialog", "Confirm button clicked")
            val email = binding.emailInput.text.toString().trim()
            if (email.isBlank()) {
                Toast.makeText(requireContext(), "请输入邮箱地址", Toast.LENGTH_SHORT).show()
                return@setOnClickListener
            }
            
            planId?.let { id ->
                viewModel.inviteFriend(id, email)
            }
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
