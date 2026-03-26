package com.weightloss.betting.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.UpdateUserRequest
import com.weightloss.betting.data.model.User
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class EditProfileState {
    object Idle : EditProfileState()
    object Loading : EditProfileState()
    data class Success(val user: User) : EditProfileState()
    data class Error(val message: String) : EditProfileState()
}

@HiltViewModel
class EditProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    
    private val _editProfileState = MutableLiveData<EditProfileState>(EditProfileState.Idle)
    val editProfileState: LiveData<EditProfileState> = _editProfileState
    
    private val _currentUser = MutableLiveData<User?>()
    val currentUser: LiveData<User?> = _currentUser
    
    fun loadUserProfile(userId: String) {
        viewModelScope.launch {
            when (val result = userRepository.getUserProfile(userId)) {
                is NetworkResult.Success -> {
                    _currentUser.value = result.data
                }
                is NetworkResult.Error -> {
                    _editProfileState.value = EditProfileState.Error(
                        result.exception.message ?: "加载用户信息失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Ignore
                }
            }
        }
    }
    
    fun updateProfile(
        userId: String,
        nickname: String,
        gender: String,
        age: String,
        height: String,
        currentWeight: String,
        targetWeight: String?
    ) {
        // Validate inputs
        if (nickname.isBlank()) {
            _editProfileState.value = EditProfileState.Error("昵称不能为空")
            return
        }
        
        if (nickname.length < 2 || nickname.length > 20) {
            _editProfileState.value = EditProfileState.Error("昵称长度必须在2-20个字符之间")
            return
        }
        
        val ageInt = age.toIntOrNull()
        if (ageInt == null || ageInt < 13 || ageInt > 120) {
            _editProfileState.value = EditProfileState.Error("年龄必须在13-120之间")
            return
        }
        
        val heightDouble = height.toDoubleOrNull()
        if (heightDouble == null || heightDouble < 100 || heightDouble > 250) {
            _editProfileState.value = EditProfileState.Error("身高必须在100-250cm之间")
            return
        }
        
        val currentWeightDouble = currentWeight.toDoubleOrNull()
        if (currentWeightDouble == null || currentWeightDouble < 30 || currentWeightDouble > 300) {
            _editProfileState.value = EditProfileState.Error("体重必须在30-300kg之间")
            return
        }
        
        val targetWeightDouble = if (!targetWeight.isNullOrBlank()) {
            val tw = targetWeight.toDoubleOrNull()
            if (tw == null || tw < 30 || tw > 300) {
                _editProfileState.value = EditProfileState.Error("目标体重必须在30-300kg之间")
                return
            }
            tw
        } else {
            null
        }
        
        // Create update request
        val request = UpdateUserRequest(
            nickname = nickname,
            gender = gender,
            age = ageInt,
            height = heightDouble,
            currentWeight = currentWeightDouble,
            targetWeight = targetWeightDouble
        )
        
        viewModelScope.launch {
            _editProfileState.value = EditProfileState.Loading
            
            when (val result = userRepository.updateUserProfile(userId, request)) {
                is NetworkResult.Success -> {
                    _editProfileState.value = EditProfileState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _editProfileState.value = EditProfileState.Error(
                        result.exception.message ?: "更新用户信息失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
