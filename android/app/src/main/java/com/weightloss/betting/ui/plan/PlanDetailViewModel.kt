package com.weightloss.betting.ui.plan

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.AcceptPlanRequest
import com.weightloss.betting.data.model.BettingPlan
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.BettingPlanRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class PlanDetailState {
    object Loading : PlanDetailState()
    data class Success(val plan: BettingPlan) : PlanDetailState()
    data class Error(val message: String) : PlanDetailState()
}

sealed class AcceptPlanState {
    object Idle : AcceptPlanState()
    object Loading : AcceptPlanState()
    object Success : AcceptPlanState()
    data class Error(val message: String) : AcceptPlanState()
    data class PaymentRequired(val requiredAmount: Double, val message: String) : AcceptPlanState()
}

sealed class RevokePlanState {
    object Idle : RevokePlanState()
    object Loading : RevokePlanState()
    object Success : RevokePlanState()
    data class Error(val message: String) : RevokePlanState()
}

sealed class ConfirmPlanState {
    object Idle : ConfirmPlanState()
    object Loading : ConfirmPlanState()
    object Success : ConfirmPlanState()
    data class Error(val message: String) : ConfirmPlanState()
}

@HiltViewModel
class PlanDetailViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository,
    private val tokenManager: com.weightloss.betting.data.remote.TokenManager
) : ViewModel() {
    
    private val _planDetailState = MutableLiveData<PlanDetailState>()
    val planDetailState: LiveData<PlanDetailState> = _planDetailState
    
    private val _acceptPlanState = MutableLiveData<AcceptPlanState>(AcceptPlanState.Idle)
    val acceptPlanState: LiveData<AcceptPlanState> = _acceptPlanState
    
    private val _revokePlanState = MutableLiveData<RevokePlanState>(RevokePlanState.Idle)
    val revokePlanState: LiveData<RevokePlanState> = _revokePlanState
    
    private val _confirmPlanState = MutableLiveData<ConfirmPlanState>(ConfirmPlanState.Idle)
    val confirmPlanState: LiveData<ConfirmPlanState> = _confirmPlanState
    
    fun getCurrentUserId(): String {
        return kotlinx.coroutines.runBlocking {
            tokenManager.getUserId() ?: ""
        }
    }
    
    fun loadPlanDetail(planId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _planDetailState.value = PlanDetailState.Loading
            
            when (val result = bettingPlanRepository.getPlanDetails(planId, forceRefresh)) {
                is NetworkResult.Success -> {
                    _planDetailState.value = PlanDetailState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _planDetailState.value = PlanDetailState.Error(
                        result.exception.message ?: "加载计划详情失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
    
    fun acceptPlan(
        planId: String,
        initialWeight: String,
        targetWeight: String
    ) {
        // Validate inputs
        val initialWeightDouble = initialWeight.toDoubleOrNull()
        if (initialWeightDouble == null || initialWeightDouble < 30 || initialWeightDouble > 300) {
            _acceptPlanState.value = AcceptPlanState.Error("初始体重必须在30-300kg之间")
            return
        }
        
        val targetWeightDouble = targetWeight.toDoubleOrNull()
        if (targetWeightDouble == null || targetWeightDouble < 30 || targetWeightDouble > 300) {
            _acceptPlanState.value = AcceptPlanState.Error("目标体重必须在30-300kg之间")
            return
        }
        
        if (targetWeightDouble >= initialWeightDouble) {
            _acceptPlanState.value = AcceptPlanState.Error("目标体重必须小于初始体重")
            return
        }
        
        val targetWeightLoss = initialWeightDouble - targetWeightDouble
        
        val request = AcceptPlanRequest(
            initialWeight = initialWeightDouble,
            targetWeight = targetWeightDouble
        )
        
        viewModelScope.launch {
            _acceptPlanState.value = AcceptPlanState.Loading
            
            when (val result = bettingPlanRepository.acceptPlan(planId, request)) {
                is NetworkResult.Success -> {
                    _acceptPlanState.value = AcceptPlanState.Success
                }
                is NetworkResult.Error -> {
                    // 检查是否是余额不足错误
                    when (val exception = result.exception) {
                        is com.weightloss.betting.data.remote.NetworkException.PaymentRequiredError -> {
                            _acceptPlanState.value = AcceptPlanState.PaymentRequired(
                                requiredAmount = exception.requiredAmount,
                                message = exception.message ?: "余额不足，需要充值"
                            )
                        }
                        else -> {
                            _acceptPlanState.value = AcceptPlanState.Error(
                                exception.message ?: "接受计划失败"
                            )
                        }
                    }
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
    
    fun rejectPlan(planId: String) {
        viewModelScope.launch {
            _acceptPlanState.value = AcceptPlanState.Loading
            
            when (val result = bettingPlanRepository.rejectPlan(planId)) {
                is NetworkResult.Success -> {
                    _acceptPlanState.value = AcceptPlanState.Success
                }
                is NetworkResult.Error -> {
                    _acceptPlanState.value = AcceptPlanState.Error(
                        result.exception.message ?: "拒绝计划失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
    
    fun revokePlan(planId: String) {
        viewModelScope.launch {
            _revokePlanState.value = RevokePlanState.Loading
            
            when (val result = bettingPlanRepository.revokePlan(planId)) {
                is NetworkResult.Success -> {
                    _revokePlanState.value = RevokePlanState.Success
                }
                is NetworkResult.Error -> {
                    _revokePlanState.value = RevokePlanState.Error(
                        result.exception.message ?: "撤销计划失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
    
    fun confirmPlan(planId: String) {
        viewModelScope.launch {
            _confirmPlanState.value = ConfirmPlanState.Loading
            
            when (val result = bettingPlanRepository.confirmPlan(planId)) {
                is NetworkResult.Success -> {
                    _confirmPlanState.value = ConfirmPlanState.Success
                }
                is NetworkResult.Error -> {
                    _confirmPlanState.value = ConfirmPlanState.Error(
                        result.exception.message ?: "确认计划失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
