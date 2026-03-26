package com.weightloss.betting.ui.plan

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.BettingPlan
import com.weightloss.betting.data.model.CreatePlanRequest
import com.weightloss.betting.data.remote.NetworkException
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.BettingPlanRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

sealed class CreatePlanState {
    object Idle : CreatePlanState()
    object Loading : CreatePlanState()
    data class Success(val plan: BettingPlan) : CreatePlanState()
    data class Error(val message: String) : CreatePlanState()
    data class PaymentRequired(val requiredAmount: Double, val message: String) : CreatePlanState()
}

@HiltViewModel
class CreatePlanViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository
) : ViewModel() {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.CHINA)
    
    private fun formatToString(date: Date): String {
        return dateFormat.format(date)
    }
    
    private val _createPlanState = MutableLiveData<CreatePlanState>(CreatePlanState.Idle)
    val createPlanState: LiveData<CreatePlanState> = _createPlanState
    
    fun createPlan(
        betAmount: String,
        startDate: Date,
        endDate: Date,
        initialWeight: String,
        targetWeight: String,
        description: String?
    ) {
        // Validate inputs
        val betAmountDouble = betAmount.toDoubleOrNull()
        if (betAmountDouble == null || betAmountDouble <= 0) {
            _createPlanState.value = CreatePlanState.Error("赌金必须大于0")
            return
        }
        
        if (endDate.before(startDate)) {
            _createPlanState.value = CreatePlanState.Error("结束日期必须晚于开始日期")
            return
        }
        
        val daysDiff = (endDate.time - startDate.time) / (1000 * 60 * 60 * 24)
        if (daysDiff > 365) {
            _createPlanState.value = CreatePlanState.Error("计划时长不能超过365天")
            return
        }
        
        val initialWeightDouble = initialWeight.toDoubleOrNull()
        if (initialWeightDouble == null || initialWeightDouble < 30 || initialWeightDouble > 300) {
            _createPlanState.value = CreatePlanState.Error("初始体重必须在30-300kg之间")
            return
        }
        
        val targetWeightDouble = targetWeight.toDoubleOrNull()
        if (targetWeightDouble == null || targetWeightDouble < 30 || targetWeightDouble > 300) {
            _createPlanState.value = CreatePlanState.Error("目标体重必须在30-300kg之间")
            return
        }
        
        if (targetWeightDouble >= initialWeightDouble) {
            _createPlanState.value = CreatePlanState.Error("目标体重必须小于初始体重")
            return
        }
        
        val targetWeightLoss = initialWeightDouble - targetWeightDouble
        
        // Create request
        val request = CreatePlanRequest(
            betAmount = betAmountDouble,
            startDate = formatToString(startDate),
            endDate = formatToString(endDate),
            initialWeight = initialWeightDouble,
            targetWeight = targetWeightDouble,
            description = description
        )
        
        viewModelScope.launch {
            _createPlanState.value = CreatePlanState.Loading
            
            when (val result = bettingPlanRepository.createPlan(request)) {
                is NetworkResult.Success -> {
                    _createPlanState.value = CreatePlanState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    // 检查是否是余额不足错误
                    when (val exception = result.exception) {
                        is NetworkException.PaymentRequiredError -> {
                            _createPlanState.value = CreatePlanState.PaymentRequired(
                                requiredAmount = exception.requiredAmount,
                                message = exception.message ?: "余额不足，需要充值"
                            )
                        }
                        else -> {
                            _createPlanState.value = CreatePlanState.Error(
                                exception.message ?: "创建计划失败"
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
}
