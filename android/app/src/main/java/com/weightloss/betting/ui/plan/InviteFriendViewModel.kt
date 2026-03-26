package com.weightloss.betting.ui.plan

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.UserSearchResult
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.BettingPlanRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class SearchState {
    object Idle : SearchState()
    object Loading : SearchState()
    data class Success(val user: UserSearchResult) : SearchState()
    data class Error(val message: String) : SearchState()
}

sealed class InviteState {
    object Idle : InviteState()
    object Loading : InviteState()
    object Success : InviteState()
    data class Error(val message: String) : InviteState()
}

@HiltViewModel
class InviteFriendViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository
) : ViewModel() {
    
    private val _searchState = MutableStateFlow<SearchState>(SearchState.Idle)
    val searchState: StateFlow<SearchState> = _searchState
    
    private val _inviteState = MutableStateFlow<InviteState>(InviteState.Idle)
    val inviteState: StateFlow<InviteState> = _inviteState
    
    fun searchFriend(email: String) {
        viewModelScope.launch {
            _searchState.value = SearchState.Loading
            
            when (val result = bettingPlanRepository.searchFriend(email)) {
                is NetworkResult.Success -> {
                    _searchState.value = SearchState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _searchState.value = SearchState.Error(
                        result.exception.message ?: "搜索失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
    
    fun inviteFriend(planId: String, email: String) {
        viewModelScope.launch {
            _inviteState.value = InviteState.Loading
            
            when (val result = bettingPlanRepository.inviteFriend(planId, email)) {
                is NetworkResult.Success -> {
                    _inviteState.value = InviteState.Success
                }
                is NetworkResult.Error -> {
                    _inviteState.value = InviteState.Error(
                        result.exception.message ?: "邀请失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
