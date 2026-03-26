package com.weightloss.betting.ui.plan

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.repository.BettingPlanRepository
import com.weightloss.betting.data.remote.NetworkResult
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 放弃计划 ViewModel
 */
@HiltViewModel
class AbandonPlanViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository
) : ViewModel() {

    private val _abandonState = MutableLiveData<AbandonState>()
    val abandonState: LiveData<AbandonState> = _abandonState

    /**
     * 放弃计划
     * @param planId 计划 ID
     * @param confirmation 确认标志
     */
    fun abandonPlan(planId: String, confirmation: Boolean = true) {
        viewModelScope.launch {
            _abandonState.value = AbandonState.Loading

            when (val result = bettingPlanRepository.abandonPlan(planId, confirmation)) {
                is NetworkResult.Success -> {
                    _abandonState.value = AbandonState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _abandonState.value = AbandonState.Error(
                        result.exception.message ?: "放弃失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}

/**
 * 放弃计划状态
 */
sealed class AbandonState {
    object Loading : AbandonState()
    data class Success(val result: com.weightloss.betting.data.model.AbandonPlanResult) : AbandonState()
    data class Error(val message: String) : AbandonState()
}
