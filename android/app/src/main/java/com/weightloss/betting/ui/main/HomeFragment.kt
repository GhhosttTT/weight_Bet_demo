package com.weightloss.betting.ui.main

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.databinding.FragmentHomeBinding
import com.weightloss.betting.ui.checkin.CheckInActivity
import com.weightloss.betting.ui.plan.CreatePlanActivity
import com.weightloss.betting.data.repository.BettingPlanRepository
import com.weightloss.betting.data.remote.NetworkResult
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class HomeFragment : Fragment() {
    
    @Inject
    lateinit var bettingPlanRepository: BettingPlanRepository
    
    @Inject
    lateinit var tokenManager: com.weightloss.betting.data.remote.TokenManager
    
    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        setupListeners()
        loadStatistics()
    }
    
    private fun setupListeners() {
        binding.btnCreatePlan.setOnClickListener {
            startActivity(Intent(requireContext(), CreatePlanActivity::class.java))
        }
        
        binding.btnCheckIn.setOnClickListener {
            startActivity(Intent(requireContext(), CheckInActivity::class.java))
        }
    }
    
    private fun loadStatistics() {
        android.util.Log.d("HomeFragment", "Loading statistics...")
        viewLifecycleOwner.lifecycleScope.launch {
            val userId = tokenManager.getUserId()
            android.util.Log.d("HomeFragment", "User ID: ${userId}")
            if (userId != null) {
                when (val result = bettingPlanRepository.getUserStatistics(userId)) {
                    is NetworkResult.Success -> {
                        val stats = result.data
                        android.util.Log.d("HomeFragment", "Stats loaded: ${stats.activePlansCount} active plans")
                        binding.tvActivePlans.text = "${stats.activePlansCount}"
                        binding.tvTotalCheckIns.text = "${stats.totalCheckInDays}"
                        // 账户余额需要从其他 API 获取，这里暂时显示 0
                        binding.tvBalance.text = "¥0.00"
                    }
                    is NetworkResult.Error -> {
                        android.util.Log.e("HomeFragment", "Failed to load stats: ${result.exception.message}")
                        // 加载失败，显示默认值
                        binding.tvActivePlans.text = "0"
                        binding.tvTotalCheckIns.text = "0"
                        binding.tvBalance.text = "¥0.00"
                    }
                    else -> {}
                }
            } else {
                android.util.Log.w("HomeFragment", "User not logged in")
                // 用户未登录，显示默认值
                binding.tvActivePlans.text = "0"
                binding.tvTotalCheckIns.text = "0"
                binding.tvBalance.text = "¥0.00"
            }
        }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
