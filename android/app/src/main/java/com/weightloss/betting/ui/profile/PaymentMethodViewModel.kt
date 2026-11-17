package com.weightloss.betting.ui.profile

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class PaymentMethodState {
    object Idle : PaymentMethodState()
    object Loading : PaymentMethodState()
    object Success : PaymentMethodState()
    data class Error(val message: String) : PaymentMethodState()
}

@HiltViewModel
class PaymentMethodViewModel @Inject constructor(
    private val userRepository: UserRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    private val _state = MutableLiveData<PaymentMethodState>(PaymentMethodState.Idle)
    val state: LiveData<PaymentMethodState> = _state

    fun bind(cardNumber: String, expiry: String, cvv: String, holder: String) {
        val digits = cardNumber.filter { it.isDigit() }
        if (digits.length !in 13..19) {
            _state.value = PaymentMethodState.Error("请输入有效的银行卡号")
            return
        }
        val expiryParts = expiry.split("/")
        val month = expiryParts.getOrNull(0)?.toIntOrNull()
        if (expiryParts.size != 2 || month == null || month !in 1..12) {
            _state.value = PaymentMethodState.Error("有效期格式应为 MM/YY")
            return
        }
        if (cvv.length !in 3..4 || !cvv.all { it.isDigit() }) {
            _state.value = PaymentMethodState.Error("请输入 3-4 位安全码")
            return
        }
        if (holder.trim().length < 2) {
            _state.value = PaymentMethodState.Error("请输入持卡人姓名")
            return
        }

        viewModelScope.launch {
            _state.value = PaymentMethodState.Loading
            val userId = tokenManager.getUserId()
            if (userId.isNullOrBlank()) {
                _state.value = PaymentMethodState.Error("登录状态已失效，请重新登录")
                return@launch
            }
            // 演示环境只保存脱敏标识；生产环境应替换为支付网关 token。
            val paymentMethodId = "card_${digits.takeLast(4)}"
            when (val result = userRepository.bindPaymentMethod(userId, paymentMethodId)) {
                is NetworkResult.Success -> _state.value = PaymentMethodState.Success
                is NetworkResult.Error -> _state.value = PaymentMethodState.Error(
                    result.exception.message ?: "绑定支付方式失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
