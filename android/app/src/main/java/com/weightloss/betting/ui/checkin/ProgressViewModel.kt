package com.weightloss.betting.ui.checkin

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.ProgressStats
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.CheckInRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class ProgressState {
    object Loading : ProgressState()
    data class Success(val stats: ProgressStats) : ProgressState()
    data class Error(val message: String) : ProgressState()
}

@HiltViewModel
class ProgressViewModel @Inject constructor(
    private val repository: CheckInRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    private val _state = MutableLiveData<ProgressState>()
    val state: LiveData<ProgressState> = _state

    fun load(planId: String) {
        viewModelScope.launch {
            val userId = tokenManager.getUserId()
            if (userId.isNullOrBlank()) {
                _state.value = ProgressState.Error("登录状态已失效，请重新登录")
                return@launch
            }
            _state.value = ProgressState.Loading
            when (val result = repository.getProgress(planId, userId)) {
                is NetworkResult.Success -> _state.value = ProgressState.Success(result.data)
                is NetworkResult.Error -> _state.value = ProgressState.Error(
                    result.exception.message ?: "加载进度失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
