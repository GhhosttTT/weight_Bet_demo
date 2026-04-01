package com.weightloss.betting.ui.main

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import com.weightloss.betting.data.model.RecommendationResponse
import com.weightloss.betting.data.repository.RecommendationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import javax.inject.Inject

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

        val cached = recommendationRepository.getCachedRecommendation()
        if (cached != null) {
            Log.d("CoachViewModel", "Found cached recommendation")
            _recommendationState.value = CoachState.Success(cached)
        } else {
            Log.d("CoachViewModel", "No cached recommendation found")
            _recommendationState.value = CoachState.Empty
        }
    }
}
