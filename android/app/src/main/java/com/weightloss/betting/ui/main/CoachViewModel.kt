package com.weightloss.betting.ui.main

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.RecommendationResponse
import com.weightloss.betting.data.remote.NetworkException
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.RecommendationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject
import kotlinx.coroutines.launch

sealed class CoachState {
    object Loading : CoachState()
    data class Success(val recommendation: RecommendationResponse) : CoachState()
    data class Error(val message: String) : CoachState()
    object Empty : CoachState()
}

@HiltViewModel
class CoachViewModel @Inject constructor(
    private val recommendationRepository: RecommendationRepository
) : ViewModel() {

    private val _recommendationState = MutableLiveData<CoachState>()
    val recommendationState: LiveData<CoachState> = _recommendationState

    fun loadRecommendation() {
        Log.d("CoachViewModel", "Loading recommendation...")
        _recommendationState.value = CoachState.Loading

        // 与 iOS 保持一致：有缓存时立即返回缓存，没有缓存时请求后端。
        // 直接读取缓存会让新用户永久停留在空状态。
        viewModelScope.launch {
            when (val result = recommendationRepository.getRecommendation(useCache = true)) {
                is NetworkResult.Success -> {
                    Log.d("CoachViewModel", "Recommendation loaded successfully")
                    _recommendationState.value = CoachState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    Log.e("CoachViewModel", "Failed to load recommendation", result.exception)
                    val message = when (result.exception) {
                        is NetworkException.NetworkError -> "网络连接失败，请稍后重试"
                        is NetworkException.TimeoutError -> "请求超时，请稍后重试"
                        else -> result.exception.message ?: "推荐加载失败"
                    }
                    _recommendationState.value = CoachState.Error(message)
                }
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
