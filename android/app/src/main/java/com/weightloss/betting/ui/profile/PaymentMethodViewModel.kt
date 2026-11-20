package com.weightloss.betting.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.PaymentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class PaymentMethodState {
    object Idle : PaymentMethodState()
    object Loading : PaymentMethodState()
    data class SetupIntentReady(val clientSecret: String) : PaymentMethodState()
    object Success : PaymentMethodState()
    data class Error(val message: String) : PaymentMethodState()
}

@HiltViewModel
class PaymentMethodViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    private val _state = MutableLiveData<PaymentMethodState>(PaymentMethodState.Idle)
    val state: LiveData<PaymentMethodState> = _state

    fun createSetupIntent() {
        viewModelScope.launch {
            _state.value = PaymentMethodState.Loading
            if (tokenManager.getUserId().isNullOrBlank()) {
                _state.value = PaymentMethodState.Error("登录状态已失效，请重新登录")
                return@launch
            }
            when (val result = paymentRepository.createSetupIntent()) {
                is NetworkResult.Success -> {
                    val secret = result.data.clientSecret
                    if (secret.isNullOrBlank()) {
                        _state.value = PaymentMethodState.Error("支付方式初始化缺少确认凭证")
                    } else {
                        _state.value = PaymentMethodState.SetupIntentReady(secret)
                    }
                }
                is NetworkResult.Error -> _state.value = PaymentMethodState.Error(
                    result.exception.message ?: "支付方式初始化失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }

    fun setupCompleted() {
        _state.value = PaymentMethodState.Success
    }

    fun setupCanceled() {
        _state.value = PaymentMethodState.Idle
    }

    fun setupFailed(message: String) {
        _state.value = PaymentMethodState.Error(message)
    }
}
