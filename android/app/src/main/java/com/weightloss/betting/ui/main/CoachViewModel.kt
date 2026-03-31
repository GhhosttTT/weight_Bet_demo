package com.weightloss.betting.ui.main

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.RecommendationResponse
import com.weightloss.betting.data.repository.RecommendationRepository
import com.weightloss.betting.data.remote.NetworkResult
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class CoachState {
    object Loading : CoachState()
    data class Success(val recommendation: RecommendationResponse) : CoachState()
    data class Error(val message: String) : CoachState()
}

@HiltViewModel
class CoachViewModel @Inject constructor(
    private val recommendationRepository: RecommendationRepository
) : ViewModel() {
    
    private val _recommendationState = MutableLiveData<CoachState>()
    val recommendationState: LiveData<CoachState> = _recommendationState
    
    fun loadRecommendation() {
        viewModelScope.launch {
            _recommendationState.value = CoachState.Loading
            
            when (val result = recommendationRepository.getRecommendation()) {
                is NetworkResult.Success -> {
                    _recommendationState.value = CoachState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _recommendationState.value = CoachState.Error(
                        result.exception.message ?: "获取推荐失败"
                    )
                }
                else -> {}
            }
        }
    }
    
    fun refreshRecommendation() {
        viewModelScope.launch {
            _recommendationState.value = CoachState.Loading
            
            when (val result = recommendationRepository.refreshRecommendation()) {
                is NetworkResult.Success -> {
                    _recommendationState.value = CoachState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _recommendationState.value = CoachState.Error(
                        result.exception.message ?: "刷新推荐失败"
                    )
                }
                else -> {}
            }
        }
    }
}
