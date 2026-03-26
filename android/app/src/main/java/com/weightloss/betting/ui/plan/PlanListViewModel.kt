package com.weightloss.betting.ui.plan

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.BettingPlan
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.BettingPlanRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class PlanListState {
    object Loading : PlanListState()
    data class Success(val plans: List<BettingPlan>) : PlanListState()
    data class Error(val message: String) : PlanListState()
}

@HiltViewModel
class PlanListViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository
) : ViewModel() {
    
    private val _planListState = MutableLiveData<PlanListState>()
    val planListState: LiveData<PlanListState> = _planListState
    
    fun loadPlans(userId: String, status: String? = null, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _planListState.value = PlanListState.Loading
            
            when (val result = bettingPlanRepository.getUserPlans(userId, status, forceRefresh)) {
                is NetworkResult.Success -> {
                    _planListState.value = PlanListState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _planListState.value = PlanListState.Error(
                        result.exception.message ?: "加载计划列表失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
