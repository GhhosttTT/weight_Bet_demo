package com.weightloss.betting.ui.plan

import android.content.Intent
import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.lifecycle.lifecycleScope
import androidx.recyclerview.widget.LinearLayoutManager
import com.weightloss.betting.R
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.databinding.FragmentPlanListBinding
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class PlanListFragment : Fragment() {
    
    private var _binding: FragmentPlanListBinding? = null
    private val binding get() = _binding!!
    private val viewModel: PlanListViewModel by viewModels()
    private lateinit var adapter: PlanAdapter
    
    @Inject
    lateinit var tokenManager: TokenManager
    
    private var userId: String? = null
    private var currentStatus: String? = null
    
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPlanListBinding.inflate(inflater, container, false)
        return binding.root
    }
    
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        
        setupRecyclerView()
        setupObservers()
        setupListeners()
        loadPlans()
    }
    
    private fun loadPlans() {
        lifecycleScope.launch {
            userId = tokenManager.getUserId()
            if (userId != null) {
                viewModel.loadPlans(userId!!)
            } else {
                Toast.makeText(requireContext(), "用户未登录", Toast.LENGTH_SHORT).show()
            }
        }
    }
    
    private fun setupRecyclerView() {
        adapter = PlanAdapter { plan ->
            val intent = Intent(requireContext(), PlanDetailActivity::class.java)
            intent.putExtra("PLAN_ID", plan.id)
            startActivity(intent)
        }
        
        binding.recyclerViewPlans.layoutManager = LinearLayoutManager(requireContext())
        binding.recyclerViewPlans.adapter = adapter
    }
    
    private fun setupObservers() {
        viewModel.planListState.observe(viewLifecycleOwner) { state ->
            when (state) {
                is PlanListState.Loading -> {
                    binding.swipeRefresh.isRefreshing = true
                    binding.tvEmptyState.visibility = View.GONE
                }
                is PlanListState.Success -> {
                    binding.swipeRefresh.isRefreshing = false
                    if (state.plans.isEmpty()) {
                        binding.tvEmptyState.visibility = View.VISIBLE
                        binding.recyclerViewPlans.visibility = View.GONE
                    } else {
                        binding.tvEmptyState.visibility = View.GONE
                        binding.recyclerViewPlans.visibility = View.VISIBLE
                        adapter.submitList(state.plans)
                    }
                }
                is PlanListState.Error -> {
                    binding.swipeRefresh.isRefreshing = false
                    Toast.makeText(requireContext(), state.message, Toast.LENGTH_LONG).show()
                }
            }
        }
    }
    
    private fun setupListeners() {
        binding.swipeRefresh.setOnRefreshListener {
            userId?.let {
                viewModel.loadPlans(it, currentStatus, forceRefresh = true)
            }
        }
        
        binding.chipGroupStatus.setOnCheckedChangeListener { _, checkedId ->
            currentStatus = when (checkedId) {
                R.id.chipPending -> "pending"
                R.id.chipActive -> "active"
                R.id.chipCompleted -> "completed"
                else -> null
            }
            userId?.let {
                viewModel.loadPlans(it, currentStatus)
            }
        }
        
        binding.fabCreatePlan.setOnClickListener {
            val intent = Intent(requireContext(), CreatePlanActivity::class.java)
            startActivity(intent)
        }
    }
    
    override fun onResume() {
        super.onResume()
        // 每次返回时刷新计划列表
        userId?.let { viewModel.loadPlans(it, currentStatus, forceRefresh = true) }
    }
    
    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
