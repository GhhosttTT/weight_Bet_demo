package com.weightloss.betting.ui.payment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.WithdrawRequest
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.PaymentRepository
import com.weightloss.betting.data.repository.UserRepository
import com.weightloss.betting.data.remote.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class WithdrawState {
    object Idle : WithdrawState()
    object Loading : WithdrawState()
    object Success : WithdrawState()
    data class Error(val message: String) : WithdrawState()
}

@HiltViewModel
class WithdrawViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository,
    private val userRepository: UserRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _withdrawState = MutableLiveData<WithdrawState>(WithdrawState.Idle)
    val withdrawState: LiveData<WithdrawState> = _withdrawState
    
    fun createWithdraw(amount: String) {
        // Validate amount
        val amountDouble = amount.toDoubleOrNull()
        if (amountDouble == null || amountDouble <= 0) {
            _withdrawState.value = WithdrawState.Error("提现金额必须大于0")
            return
        }
        
        if (amountDouble < 0.01) {
            _withdrawState.value = WithdrawState.Error("提现金额不能少于0.01元")
            return
        }
        
        if (amountDouble > 50000) {
            _withdrawState.value = WithdrawState.Error("单次提现金额不能超过50000元")
            return
        }
        
        viewModelScope.launch {
            _withdrawState.value = WithdrawState.Loading

            val userId = tokenManager.getUserId()
            if (userId.isNullOrBlank()) {
                _withdrawState.value = WithdrawState.Error("登录状态已失效，请重新登录")
                return@launch
            }

            val profileResult = userRepository.getUserProfile(userId, forceRefresh = true)
            if (profileResult is NetworkResult.Error) {
                _withdrawState.value = WithdrawState.Error(profileResult.exception.message ?: "读取提现方式失败")
                return@launch
            }
            val paymentMethodId = (profileResult as? NetworkResult.Success)?.data?.paymentMethodId
            if (paymentMethodId.isNullOrBlank()) {
                _withdrawState.value = WithdrawState.Error("请先绑定提现方式")
                return@launch
            }

            val request = WithdrawRequest(amount = amountDouble, paymentMethodId = paymentMethodId)
            when (val result = paymentRepository.withdraw(request)) {
                is NetworkResult.Success -> {
                    _withdrawState.value = WithdrawState.Success
                }
                is NetworkResult.Error -> {
                    _withdrawState.value = WithdrawState.Error(
                        result.exception.message ?: "提现申请失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
