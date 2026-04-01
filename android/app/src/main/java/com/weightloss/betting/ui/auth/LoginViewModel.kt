package com.weightloss.betting.ui.auth

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.LoginRequest
import com.weightloss.betting.data.model.User
import com.weightloss.betting.data.remote.NetworkException
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.AuthRepository
import com.weightloss.betting.data.repository.RecommendationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository,
    private val recommendationRepository: RecommendationRepository
) : ViewModel() {
    
    private val _loginState = MutableLiveData<LoginState>()
    val loginState: LiveData<LoginState> = _loginState
    
    private val _user = MutableLiveData<User>()
    val user: LiveData<User> = _user
    
    fun login(email: String, password: String) {
        Log.d("LoginViewModel", "login() called with email: $email")
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
        
        Log.d("LoginViewModel", "Setting login state to Loading")
        _loginState.value = LoginState.Loading
        
        viewModelScope.launch {
            Log.d("LoginViewModel", "Starting authRepository.login()")
            val request = LoginRequest(email, password)
            
            when (val result = authRepository.login(request)) {
                is NetworkResult.Success -> {
                    Log.d("LoginViewModel", "Login successful!")
                    Log.d("LoginViewModel", "Setting login state to Success")
                    _loginState.value = LoginState.Success
                    Log.d("LoginViewModel", "Starting fetchAndCacheRecommendationAsync()")
                    recommendationRepository.fetchAndCacheRecommendationAsync()
                }
                is NetworkResult.Error -> {
                    Log.e("LoginViewModel", "Login error: ${result.exception.message}")
                    val errorMessage = when (result.exception) {
                        is NetworkException.UnauthorizedError -> "邮箱或密码错误"
                        is NetworkException.NetworkError -> "网络连接失败，请检查网络"
                        is NetworkException.TimeoutError -> "请求超时，请重试"
                        else -> result.exception.message ?: "登录失败"
                    }
                    _loginState.value = LoginState.Error(errorMessage)
                }
                is NetworkResult.Loading -> {
                    Log.d("LoginViewModel", "Login result is Loading")
                }
            }
        }
    }
    
    fun googleLogin(idToken: String) {
        Log.d("LoginViewModel", "googleLogin() called")
        _loginState.value = LoginState.Loading
            
        viewModelScope.launch {
            when (val result = authRepository.googleLogin(idToken)) {
                is NetworkResult.Success -> {
                    Log.d("LoginViewModel", "Google login successful!")
                    _loginState.value = LoginState.Success
                    recommendationRepository.fetchAndCacheRecommendationAsync()
                }
                is NetworkResult.Error -> {
                    Log.e("LoginViewModel", "Google login error: ${result.exception.message}")
                    val errorMessage = when (result.exception) {
                        is NetworkException.NetworkError -> "网络连接失败，请检查网络"
                        is NetworkException.TimeoutError -> "请求超时，请重试"
                        else -> result.exception.message ?: "Google 登录失败"
                    }
                    _loginState.value = LoginState.Error(errorMessage)
                }
                is NetworkResult.Loading -> {
                }
            }
        }
    }
    
    private fun isValidEmail(email: String): Boolean {
        return android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()
    }
}

sealed class LoginState {
    object Loading : LoginState()
    object Success : LoginState()
    data class Error(val message: String) : LoginState()
}
