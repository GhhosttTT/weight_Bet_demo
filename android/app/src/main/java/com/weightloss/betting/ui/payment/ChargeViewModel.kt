package com.weightloss.betting.ui.payment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.ChargeRequest
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.PaymentRepository
import com.weightloss.betting.data.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class ChargeState {
    object Idle : ChargeState()
    object Loading : ChargeState()
    data class Success(val clientSecret: String) : ChargeState()
    data class Error(val message: String) : ChargeState()
}

@HiltViewModel
class ChargeViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository,
    private val userRepository: UserRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _chargeState = MutableLiveData<ChargeState>(ChargeState.Idle)
    val chargeState: LiveData<ChargeState> = _chargeState
    
    fun createCharge(amount: String) {
        // Validate amount
        val amountDouble = amount.toDoubleOrNull()
        if (amountDouble == null || amountDouble <= 0) {
            _chargeState.value = ChargeState.Error("充值金额必须大于0")
            return
        }
        
        if (amountDouble < 1) {
            _chargeState.value = ChargeState.Error("充值金额不能少于1元")
            return
        }
        
        if (amountDouble > 10000) {
            _chargeState.value = ChargeState.Error("单次充值金额不能超过10000元")
            return
        }
        
        val request = ChargeRequest(amount = amountDouble, paymentMethodId = "default")
        
        viewModelScope.launch {
            _chargeState.value = ChargeState.Loading
            
            when (val result = paymentRepository.charge(request)) {
                is NetworkResult.Success -> {
                    // Clear user cache after successful charge
                    userRepository.clearCache()
                    
                    // Optionally refresh balance to get the latest value
                    val userId = tokenManager.getUserId()
                    if (userId != null) {
                        userRepository.getBalance(userId)
                    }
                    
                    _chargeState.value = ChargeState.Success(result.data.transactionId ?: "")
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
}
