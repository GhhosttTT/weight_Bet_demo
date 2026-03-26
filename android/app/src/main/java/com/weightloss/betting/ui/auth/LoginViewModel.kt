package com.weightloss.betting.ui.auth

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.LoginRequest
import com.weightloss.betting.data.model.User
import com.weightloss.betting.data.remote.NetworkException
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

/**
 * 登录 ViewModel
 */
@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _loginState = MutableLiveData<LoginState>()
    val loginState: LiveData<LoginState> = _loginState
    
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user
    
    /**
     * 用户登录
     */
    fun login(email: String, password: String) {
        // 验证输入
        if (email.isBlank()) {
            _loginState.value = LoginState.Error("请输入邮箱")
            return
        }
        
        if (password.isBlank()) {
            _loginState.value = LoginState.Error("请输入密码")
            return
        }
        
        if (!isValidEmail(email)) {
            _loginState.value = LoginState.Error("邮箱格式不正确")
            return
        }
        
        _loginState.value = LoginState.Loading
        
        viewModelScope.launch {
            val request = LoginRequest(email, password)
            
            when (val result = authRepository.login(request)) {
                is NetworkResult.Success -> {
                    // 登录成功，Token 已保存
                    _loginState.value = LoginState.Success
                }
                is NetworkResult.Error -> {
                    val errorMessage = when (result.exception) {
                        is NetworkException.UnauthorizedError -> "邮箱或密码错误"
                        is NetworkException.NetworkError -> "网络连接失败，请检查网络"
                        is NetworkException.TimeoutError -> "请求超时，请重试"
                        else -> result.exception.message ?: "登录失败"
                    }
                    _loginState.value = LoginState.Error(errorMessage)
                }
                is NetworkResult.Loading -> {
                    // 已经设置为 Loading 状态
                }
            }
        }
    }
    
    /**
     * Google 登录
     */
    fun googleLogin(idToken: String) {
        _loginState.value = LoginState.Loading
            
        viewModelScope.launch {
            when (val result = authRepository.googleLogin(idToken)) {
                is NetworkResult.Success -> {
                    // 登录成功，Token 已保存
                    _loginState.value = LoginState.Success
                }
                is NetworkResult.Error -> {
                    val errorMessage = when (result.exception) {
                        is NetworkException.NetworkError -> "网络连接失败，请检查网络"
                        is NetworkException.TimeoutError -> "请求超时，请重试"
                        else -> result.exception.message ?: "Google 登录失败"
                    }
                    _loginState.value = LoginState.Error(errorMessage)
                }
                is NetworkResult.Loading -> {
                    // 已经设置为 Loading 状态
                }
            }
        }
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}

/**
 * 登录状态
 */
sealed class LoginState {
    object Loading : LoginState()
    object Success : LoginState()
    data class Error(val message: String) : LoginState()
}
