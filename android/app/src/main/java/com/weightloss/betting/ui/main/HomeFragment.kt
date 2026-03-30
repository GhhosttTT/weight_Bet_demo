package com.weightloss.betting.ui.main

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.data.model.BettingPlan
import com.weightloss.betting.databinding.FragmentHomeBinding
import com.weightloss.betting.ui.checkin.CheckInActivity
import com.weightloss.betting.ui.plan.CreatePlanActivity
import com.weightloss.betting.data.repository.BettingPlanRepository
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class HomeFragment : Fragment() {
    
    @Inject
    lateinit var bettingPlanRepository: BettingPlanRepository
    
    @Inject
    lateinit var tokenManager: TokenManager
    
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
            checkIn()
        }
    }
    
    private fun checkIn() {
        lifecycleScope.launch {
            val userId = tokenManager.getUserId()
            if (userId == null) {
                Toast.makeText(requireContext(), "请先登录", Toast.LENGTH_SHORT).show()
                return@launch
            }
            
            when (val result = bettingPlanRepository.getUserPlans(userId, "active", forceRefresh = true)) {
                is NetworkResult.Success -> {
                    val activePlans = result.data
                    when {
                        activePlans.isEmpty() -> {
                            Toast.makeText(requireContext(), "没有进行中的计划", Toast.LENGTH_SHORT).show()
                        }
                        activePlans.size == 1 -> {
                            startCheckInActivity(activePlans[0].id)
                        }
                        else -> {
                            showPlanSelectionDialog(activePlans)
                        }
                    }
                }
                is NetworkResult.Error -> {
                    Toast.makeText(requireContext(), "获取计划列表失败: ${result.exception.message}", Toast.LENGTH_SHORT).show()
                }
                else -> {}
            }
        }
    }
    
    private fun showPlanSelectionDialog(plans: List<BettingPlan>) {
        val planNames = plans.map { plan ->
            val creatorName = plan.creatorNickname ?: plan.creatorEmail ?: "创建者"
            val participantName = plan.participantNickname ?: plan.participantEmail ?: "参与者"
            "$creatorName vs $participantName"
        }.toTypedArray()
        
        AlertDialog.Builder(requireContext())
            .setTitle("选择要打卡的计划")
            .setItems(planNames) { _, which ->
                startCheckInActivity(plans[which].id)
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    private fun startCheckInActivity(planId: String) {
        val intent = Intent(requireContext(), CheckInActivity::class.java)
        intent.putExtra("PLAN_ID", planId)
        startActivity(intent)
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
                        android.util.Log.d("HomeFragment", "Stats loaded: ${stats.activePlansCount} active plans, ${stats.totalCheckInDays} check-ins")
                        binding.tvActivePlans.text = "${stats.activePlansCount}"
                        binding.tvTotalCheckIns.text = "${stats.totalCheckInDays}"
                        binding.tvBalance.text = "¥0.00"
                    }
                    is NetworkResult.Error -> {
                        android.util.Log.e("HomeFragment", "Failed to load stats: ${result.exception.message}")
                        binding.tvActivePlans.text = "0"
                        binding.tvTotalCheckIns.text = "0"
                        binding.tvBalance.text = "¥0.00"
                    }
                    else -> {}
                }
            } else {
                android.util.Log.w("HomeFragment", "User not logged in")
                binding.tvActivePlans.text = "0"
                binding.tvTotalCheckIns.text = "0"
                binding.tvBalance.text = "¥0.00"
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        // 每次返回首页时刷新统计数据
        loadStatistics()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
