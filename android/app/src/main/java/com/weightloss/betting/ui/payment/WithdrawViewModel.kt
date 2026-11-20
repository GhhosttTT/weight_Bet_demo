package com.weightloss.betting.ui.payment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.WithdrawRequest
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.PaymentRepository
import com.weightloss.betting.data.remote.TokenManager
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class WithdrawState {
    object Idle : WithdrawState()
    object Loading : WithdrawState()
    object Success : WithdrawState()
    data class OnboardingReady(val url: String) : WithdrawState()
    data class Error(val message: String) : WithdrawState()
}

@HiltViewModel
class WithdrawViewModel @Inject constructor(
    private val paymentRepository: PaymentRepository,
    private val tokenManager: TokenManager
) : ViewModel() {
    
    private val _withdrawState = MutableLiveData<WithdrawState>(WithdrawState.Idle)
    val withdrawState: LiveData<WithdrawState> = _withdrawState

    private val _availableBalance = MutableLiveData(0.0)
    val availableBalance: LiveData<Double> = _availableBalance

    fun loadAvailableBalance() {
        viewModelScope.launch {
            val userId = tokenManager.getUserId()
            if (userId.isNullOrBlank()) {
                _withdrawState.value = WithdrawState.Error("登录状态已失效，请重新登录")
                return@launch
            }
            when (val result = paymentRepository.getBalance(userId)) {
                is NetworkResult.Success -> _availableBalance.value = result.data.availableBalance
                is NetworkResult.Error -> _withdrawState.value = WithdrawState.Error(
                    result.exception.message ?: "无法加载可用余额"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }

    fun startConnectOnboarding() {
        viewModelScope.launch {
            _withdrawState.value = WithdrawState.Loading
            when (val result = paymentRepository.createConnectOnboardingLink()) {
                is NetworkResult.Success -> _withdrawState.value = WithdrawState.OnboardingReady(result.data.url)
                is NetworkResult.Error -> _withdrawState.value = WithdrawState.Error(
                    result.exception.message ?: "无法创建提现账户认证链接"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }
    
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

            // Stripe 模式使用 Connect 账户，不再把银行卡后四位当作提现凭证。
            val request = WithdrawRequest(amount = amountDouble, paymentMethodId = "")
            when (val result = paymentRepository.withdraw(request)) {
                is NetworkResult.Success -> {
                    _availableBalance.value = (_availableBalance.value ?: 0.0) - amountDouble
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
