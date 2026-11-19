package com.weightloss.betting.ui.payment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.ChargeIntentRequest
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.PaymentRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import java.util.UUID
import javax.inject.Inject

sealed class ChargeState {
    object Idle : ChargeState()
    object Loading : ChargeState()
    data class AwaitingConfirmation(val clientSecret: String) : ChargeState()
    object Success : ChargeState()
    data class Error(val message: String) : ChargeState()
}

@HiltViewModel
class ChargeViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    private var chargeIdempotencyKey: String? = null
    
    private val _chargeState = MutableLiveData<ChargeState>(ChargeState.Idle)
    val chargeState: LiveData<ChargeState> = _chargeState
    
    fun createCharge(amount: String) {
        // Validate amount
        val amountDouble = amount.toDoubleOrNull()
        if (amountDouble == null || amountDouble <= 0) {
            _chargeState.value = ChargeState.Error("充值金额必须大于0")
            return
        }
        
        if (amountDouble < 0.01) {
            _chargeState.value = ChargeState.Error("充值金额不能少于0.01元")
            return
        }
        
        if (amountDouble > 10000) {
            _chargeState.value = ChargeState.Error("单次充值金额不能超过10000元")
            return
        }
        
        viewModelScope.launch {
            _chargeState.value = ChargeState.Loading

            val userId = tokenManager.getUserId()
            if (userId.isNullOrBlank()) {
                _chargeState.value = ChargeState.Error("登录状态已失效，请重新登录")
                return@launch
            }

            val idempotencyKey = chargeIdempotencyKey ?: UUID.randomUUID().toString().also {
                chargeIdempotencyKey = it
            }
            when (val result = paymentRepository.createChargeIntent(
                ChargeIntentRequest(amountDouble, idempotencyKey)
            )) {
                is NetworkResult.Success -> {
                    val secret = result.data.clientSecret
                    if (secret.isNullOrBlank()) {
                        _chargeState.value = ChargeState.Error("支付订单缺少确认凭证")
                    } else {
                        _chargeState.value = ChargeState.AwaitingConfirmation(secret)
                    }
                }
                is NetworkResult.Error -> {
                    _chargeState.value = ChargeState.Error(
                        result.exception.message ?: "创建充值订单失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }

    fun paymentCompleted() {
        chargeIdempotencyKey = null
        _chargeState.value = ChargeState.Success
    }

    fun paymentCanceled() {
        chargeIdempotencyKey = null
        _chargeState.value = ChargeState.Error("已取消支付")
    }

    fun paymentFailed(message: String) {
        _chargeState.value = ChargeState.Error(message)
    }
}
