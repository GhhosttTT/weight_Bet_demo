package com.weightloss.betting.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.User
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.UserRepository
import com.weightloss.betting.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class ProfileState {
    object Loading : ProfileState()
    data class Success(val user: User) : ProfileState()
    data class Error(val message: String) : ProfileState()
}

sealed class AccountDeletionState {
    object Idle : AccountDeletionState()
    object Loading : AccountDeletionState()
    object Success : AccountDeletionState()
    data class Error(val message: String) : AccountDeletionState()
}

@HiltViewModel
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _profileState = MutableLiveData<ProfileState>()
    val profileState: LiveData<ProfileState> = _profileState
    private val _accountDeletionState = MutableLiveData<AccountDeletionState>(AccountDeletionState.Idle)
    val accountDeletionState: LiveData<AccountDeletionState> = _accountDeletionState
    
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

    fun deleteAccount(userId: String) {
        viewModelScope.launch {
            _accountDeletionState.value = AccountDeletionState.Loading
            when (val result = userRepository.deleteUserAccount(userId)) {
                is NetworkResult.Success -> _accountDeletionState.value = AccountDeletionState.Success
                is NetworkResult.Error -> _accountDeletionState.value = AccountDeletionState.Error(
                    result.exception.message ?: "账户删除失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }

    suspend fun logout() {
        authRepository.logout()
    }
}
