package com.weightloss.betting.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.User
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class ProfileState {
    object Loading : ProfileState()
    data class Success(val user: User) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    
    private val _profileState = MutableLiveData<ProfileState>()
    val profileState: LiveData<ProfileState> = _profileState
    
    fun loadUserProfile(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _profileState.value = ProfileState.Loading
            
            when (val result = userRepository.getUserProfile(userId, forceRefresh)) {
                is NetworkResult.Success -> {
                    _profileState.value = ProfileState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _profileState.value = ProfileState.Error(
                        result.exception.message ?: "加载用户信息失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
