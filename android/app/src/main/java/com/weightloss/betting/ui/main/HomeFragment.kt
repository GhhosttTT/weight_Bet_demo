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
                        binding.tvActivePlans.text = "${stats.activePlansCount}"
                        binding.tvTotalCheckIns.text = "${stats.totalCheckInDays}"
                        binding.tvBalance.text = "¥0.00"
                    }
                    is NetworkResult.Error -> {
                        binding.tvActivePlans.text = "0"
                        binding.tvTotalCheckIns.text = "0"
                        binding.tvBalance.text = "¥0.00"
                    }
                    else -> {}
                }
            } else {
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
