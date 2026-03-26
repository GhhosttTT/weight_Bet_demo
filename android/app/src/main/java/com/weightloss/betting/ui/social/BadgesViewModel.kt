package com.weightloss.betting.ui.social

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.Badge
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.SocialRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class BadgesState {
    object Loading : BadgesState()
    data class Success(val badges: List<Badge>) : BadgesState()
    data class Error(val message: String) : BadgesState()
}

@HiltViewModel
class BadgesViewModel @Inject constructor(
    private val socialRepository: SocialRepository
) : ViewModel() {
    
    private val _badgesState = MutableLiveData<BadgesState>()
    val badgesState: LiveData<BadgesState> = _badgesState
    
    fun loadBadges(userId: String) {
        viewModelScope.launch {
            _badgesState.value = BadgesState.Loading
            
            when (val result = socialRepository.getUserBadges(userId)) {
                is NetworkResult.Success -> {
                    _badgesState.value = BadgesState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _badgesState.value = BadgesState.Error(
                        result.exception.message ?: "加载勋章失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
