package com.weightloss.betting.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.RegisterRequest
import com.weightloss.betting.data.model.User
import com.weightloss.betting.data.remote.NetworkException
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 注册 ViewModel
 */
@HiltViewModel
class RegisterViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _registerState = MutableLiveData<RegisterState>()
    val registerState: LiveData<RegisterState> = _registerState
    
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user
    
    /**
     * 用户注册
     */
    fun register(
        email: String,
        password: String,
        confirmPassword: String,
        nickname: String,
        gender: String,
        age: Int,
        height: Double,
        currentWeight: Double
    ) {
        // 验证输入
        val validationError = validateInput(
            email, password, confirmPassword, nickname, gender, age, height, currentWeight
        )
        
        if (validationError != null) {
            _registerState.value = RegisterState.Error(validationError)
            return
        }
        
        _registerState.value = RegisterState.Loading
        
        viewModelScope.launch {
            val request = RegisterRequest(
                email = email,
                password = password,
                nickname = nickname,
                gender = gender,
                age = age,
                height = height,
                currentWeight = currentWeight
            )
            
            when (val result = authRepository.register(request)) {
                is NetworkResult.Success -> {
                    // 注册成功，Token已保存
                    _registerState.value = RegisterState.Success
                }
                is NetworkResult.Error -> {
                    val errorMessage = when (result.exception) {
                        is NetworkException.ValidationError -> {
                            result.exception.message ?: "数据验证失败"
                        }
                        is NetworkException.NetworkError -> "网络连接失败,请检查网络"
                        is NetworkException.TimeoutError -> "请求超时,请重试"
                        else -> result.exception.message ?: "注册失败"
                    }
                    _registerState.value = RegisterState.Error(errorMessage)
                }
                is NetworkResult.Loading -> {
                    // 已经设置为 Loading 状态
                }
            }
        }
    }
    
    private fun validateInput(
        email: String,
        password: String,
        confirmPassword: String,
        nickname: String,
        gender: String,
        age: Int,
        height: Double,
        currentWeight: Double
    ): String? {
        if (email.isBlank()) {
            return "请输入邮箱"
        }
        
        if (!isValidEmail(email)) {
            return "邮箱格式不正确"
        }
        
        if (password.isBlank()) {
            return "请输入密码"
        }
        
        if (password.length < 8) {
            return "密码长度至少为 8 位"
        }
        
        if (password != confirmPassword) {
            return "两次输入的密码不一致"
        }
        
        if (nickname.isBlank()) {
            return "请输入昵称"
        }
        
        if (nickname.length < 2 || nickname.length > 20) {
            return "昵称长度应在 2-20 个字符之间"
        }
        
        if (gender.isBlank()) {
            return "请选择性别"
        }
        
        if (age < 13 || age > 120) {
            return "年龄应在 13-120 之间"
        }
        
        if (height < 100 || height > 250) {
            return "身高应在 100-250 cm 之间"
        }
        
        if (currentWeight < 30 || currentWeight > 300) {
            return "体重应在 30-300 kg 之间"
        }
        
        return null
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}

/**
 * 注册状态
 */
sealed class RegisterState {
    object Loading : RegisterState()
    object Success : RegisterState()
    data class Error(val message: String) : RegisterState()
}
