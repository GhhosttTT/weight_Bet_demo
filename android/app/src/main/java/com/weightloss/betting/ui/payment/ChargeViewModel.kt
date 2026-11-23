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
import kotlinx.coroutines.delay
import java.util.UUID
import javax.inject.Inject

sealed class ChargeState {
    object Idle : ChargeState()
    object Loading : ChargeState()
    data class AwaitingConfirmation(val clientSecret: String, val transactionId: String) : ChargeState()
    object AwaitingWebhook : ChargeState()
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
                        tokenManager.savePendingCharge(result.data.transactionId)
                        _chargeState.value = ChargeState.AwaitingConfirmation(secret, result.data.transactionId)
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

    fun paymentCompleted(transactionId: String) {
        _chargeState.value = ChargeState.AwaitingWebhook
        viewModelScope.launch {
            repeat(12) { attempt ->
                when (val result = paymentRepository.getTransactionStatus(transactionId)) {
                    is NetworkResult.Success -> when (result.data.status.lowercase()) {
                        "completed" -> {
                            tokenManager.clearPendingCharge()
                            chargeIdempotencyKey = null
                            _chargeState.value = ChargeState.Success
                            return@launch
                        }
                        "failed" -> {
                            tokenManager.clearPendingCharge()
                            chargeIdempotencyKey = null
                            _chargeState.value = ChargeState.Error("支付已失败，请重新尝试")
                            return@launch
                        }
                    }
                    is NetworkResult.Error -> {
                        if (attempt == 11) {
                            _chargeState.value = ChargeState.Error("支付已确认，入账处理中，请稍后刷新余额")
                            return@launch
                        }
                    }
                    is NetworkResult.Loading -> Unit
                }
                delay(1000)
            }
            _chargeState.value = ChargeState.Error("支付已确认，入账处理中，请稍后刷新余额")
        }
    }

    fun paymentCanceled() {
        // 保留服务端 pending 交易以便下次恢复，但下一次改金额必须使用新幂等键。
        chargeIdempotencyKey = null
        _chargeState.value = ChargeState.Error("已取消支付")
    }

    fun paymentFailed(message: String) {
        // Stripe 已明确拒绝当前 PaymentIntent；下一次重试必须创建新的
        // 本地交易和 Stripe 幂等键，避免重复复用已失败的 PaymentIntent。
        chargeIdempotencyKey = null
        viewModelScope.launch { tokenManager.clearPendingCharge() }
        _chargeState.value = ChargeState.Error(message)
    }

    fun restorePendingCharge() {
        viewModelScope.launch {
            val transactionId = tokenManager.getPendingCharge() ?: return@launch
            when (val result = paymentRepository.resumeChargeIntent(transactionId)) {
                is NetworkResult.Success -> {
                    if (result.data.status.equals("canceled", ignoreCase = true) ||
                        result.data.status.equals("failed", ignoreCase = true)) {
                        paymentFailed("未完成充值订单已取消，请重新发起充值")
                        return@launch
                    }
                    val secret = result.data.clientSecret
                    if (secret.isNullOrBlank()) {
                        _chargeState.value = ChargeState.Error("未完成订单缺少支付凭证")
                    } else if (result.data.status.equals("succeeded", ignoreCase = true)) {
                        paymentCompleted(transactionId)
                    } else {
                        _chargeState.value = ChargeState.AwaitingConfirmation(secret, transactionId)
                    }
                }
                is NetworkResult.Error -> {
                    _chargeState.value = ChargeState.Error("未完成充值订单恢复失败，请刷新交易记录")
                }
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
