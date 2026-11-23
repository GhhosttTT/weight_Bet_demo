package com.weightloss.betting.ui.settlement

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.SettlementSelectionStatus
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.SettlementRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class SettlementState {
    object Loading : SettlementState()
    data class Ready(val status: SettlementSelectionStatus) : SettlementState()
    data class Submitted(val status: SettlementSelectionStatus?, val refreshed: Boolean) : SettlementState()
    data class Error(val message: String) : SettlementState()
}

sealed class DisputeState {
    object Idle : DisputeState()
    object Submitting : DisputeState()
    data class Success(val dispute: com.weightloss.betting.data.model.DisputeResponse) : DisputeState()
    data class Error(val message: String) : DisputeState()
}

@HiltViewModel
class SettlementViewModel @Inject constructor(
    private val repository: SettlementRepository
) : ViewModel() {
    private val _state = MutableLiveData<SettlementState>()
    val state: LiveData<SettlementState> = _state
    private val _disputeState = MutableLiveData<DisputeState>(DisputeState.Idle)
    val disputeState: LiveData<DisputeState> = _disputeState

    fun load(planId: String) {
        viewModelScope.launch {
            _state.value = SettlementState.Loading
            when (val result = repository.getStatus(planId)) {
                is NetworkResult.Success -> _state.value = SettlementState.Ready(result.data)
                is NetworkResult.Error -> _state.value = SettlementState.Error(
                    result.exception.message ?: "加载结算状态失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }

    fun submit(planId: String, selfAchieved: Boolean, opponentAchieved: Boolean) {
        viewModelScope.launch {
            _state.value = SettlementState.Loading
            when (val result = repository.submit(planId, selfAchieved, opponentAchieved)) {
                is NetworkResult.Success -> {
                    when (val status = repository.getStatus(planId)) {
                        is NetworkResult.Success -> _state.value = SettlementState.Submitted(status.data, true)
                        is NetworkResult.Error -> _state.value = SettlementState.Submitted(null, false)
                        is NetworkResult.Loading -> Unit
                    }
                }
                is NetworkResult.Error -> _state.value = SettlementState.Error(
                    result.exception.message ?: "提交结算选择失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }

    fun submitDispute(settlementId: String, reason: String) {
        viewModelScope.launch {
            _disputeState.value = DisputeState.Submitting
            when (val result = repository.submitDispute(settlementId, reason)) {
                is NetworkResult.Success -> _disputeState.value = DisputeState.Success(result.data)
                is NetworkResult.Error -> _disputeState.value = DisputeState.Error(
                    result.exception.message ?: "提交争议失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
