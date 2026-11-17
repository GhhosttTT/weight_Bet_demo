package com.weightloss.betting.ui.checkin

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.CheckIn
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.CheckInRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class CheckInHistoryState {
    object Loading : CheckInHistoryState()
    data class Success(val items: List<CheckIn>) : CheckInHistoryState()
    data class Error(val message: String) : CheckInHistoryState()
}

@HiltViewModel
class CheckInHistoryViewModel @Inject constructor(
    private val repository: CheckInRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    private val _state = MutableLiveData<CheckInHistoryState>()
    val state: LiveData<CheckInHistoryState> = _state

    fun load(planId: String) {
        viewModelScope.launch {
            val userId = tokenManager.getUserId()
            if (userId.isNullOrBlank()) {
                _state.value = CheckInHistoryState.Error("登录状态已失效，请重新登录")
                return@launch
            }
            _state.value = CheckInHistoryState.Loading
            when (val result = repository.getCheckInHistory(planId, userId, forceRefresh = true)) {
                is NetworkResult.Success -> _state.value = CheckInHistoryState.Success(result.data)
                is NetworkResult.Error -> _state.value = CheckInHistoryState.Error(
                    result.exception.message ?: "加载打卡历史失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
