package com.weightloss.betting.ui.main

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.lifecycle.lifecycleScope
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.BettingPlanRepository
import com.weightloss.betting.databinding.FragmentHomeBinding
import com.weightloss.betting.ui.checkin.CheckInActivity
import com.weightloss.betting.ui.plan.CreatePlanActivity
import com.weightloss.betting.ui.plan.PlanListActivity
import com.weightloss.betting.data.repository.UserRepository
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class HomeFragment : Fragment() {
    
    @Inject
    lateinit var bettingPlanRepository: BettingPlanRepository
    
    @Inject
    lateinit var tokenManager: TokenManager

    @Inject
    lateinit var userRepository: UserRepository
    
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
    }
    
    private fun setupListeners() {
        binding.btnCreatePlan.setOnClickListener {
            startActivity(Intent(requireContext(), CreatePlanActivity::class.java))
        }

        binding.btnMyPlans.setOnClickListener {
            startActivity(Intent(requireContext(), PlanListActivity::class.java))
        }
        
        binding.btnCheckIn.setOnClickListener {
            checkIn()
        }
    }
    
    private fun checkIn() {
        val intent = Intent(requireContext(), CheckInActivity::class.java)
        startActivity(intent)
    }
    
    private fun loadStatistics() {
        viewLifecycleOwner.lifecycleScope.launch {
            val userId = tokenManager.getUserId()
            if (userId != null) {
                when (val result = bettingPlanRepository.getUserStatistics(userId)) {
                    is NetworkResult.Success -> {
                        val stats = result.data
                        binding.tvCheckInStats.text = "进行中的计划：${stats.activePlansCount}"
                        loadBalance(userId)
                    }
                    is NetworkResult.Error -> {
                        binding.tvCheckInStats.text = "进行中的计划：--"
                        binding.tvBalance.text = "钱包余额：--"
                    }
                    else -> {}
                }
            } else {
                binding.tvCheckInStats.text = "进行中的计划：--"
                binding.tvBalance.text = "钱包余额：--"
            }
        }
    }

    private fun loadBalance(userId: String) {
        viewLifecycleOwner.lifecycleScope.launch {
            when (val result = userRepository.getBalance(userId)) {
                is NetworkResult.Success -> binding.tvBalance.text =
                    "钱包余额：¥%.2f".format(result.data.availableBalance)
                is NetworkResult.Error -> binding.tvBalance.text = "钱包余额：--"
                else -> Unit
            }
        }
    }
    
    override fun onResume() {
        super.onResume()
        // 首次进入和返回首页时统一在此刷新，避免重复请求。
        loadStatistics()
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
