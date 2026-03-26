package com.weightloss.betting.ui.social

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.LeaderboardEntry
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.SocialRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class LeaderboardState {
    object Loading : LeaderboardState()
    data class Success(val entries: List<LeaderboardEntry>) : LeaderboardState()
    data class Error(val message: String) : LeaderboardState()
}

@HiltViewModel
class LeaderboardViewModel @Inject constructor(
    private val socialRepository: SocialRepository
) : ViewModel() {
    
    private val _leaderboardState = MutableLiveData<LeaderboardState>()
    val leaderboardState: LiveData<LeaderboardState> = _leaderboardState
    
    fun loadLeaderboard(type: String) {
        viewModelScope.launch {
            _leaderboardState.value = LeaderboardState.Loading
            
            when (val result = socialRepository.getLeaderboard(type)) {
                is NetworkResult.Success -> {
                    _leaderboardState.value = LeaderboardState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _leaderboardState.value = LeaderboardState.Error(
                        result.exception.message ?: "加载排行榜失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
