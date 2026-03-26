package com.weightloss.betting.ui.payment

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.Balance
import com.weightloss.betting.data.model.Transaction
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.UserRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class BalanceState {
    object Loading : BalanceState()
    data class Success(val balance: Balance) : BalanceState()
    data class Error(val message: String) : BalanceState()
}

sealed class TransactionListState {
    object Loading : TransactionListState()
    data class Success(val transactions: List<Transaction>) : TransactionListState()
    data class Error(val message: String) : TransactionListState()
}

@HiltViewModel
class BalanceViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    
    private val _balanceState = MutableLiveData<BalanceState>()
    val balanceState: LiveData<BalanceState> = _balanceState
    
    private val _transactionListState = MutableLiveData<TransactionListState>()
    val transactionListState: LiveData<TransactionListState> = _transactionListState
    
    fun loadBalance(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _balanceState.value = BalanceState.Loading
            
            when (val result = userRepository.getBalance(userId)) {
                is NetworkResult.Success -> {
                    _balanceState.value = BalanceState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _balanceState.value = BalanceState.Error(
                        result.exception.message ?: "加载余额失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
    
    fun loadTransactions(userId: String, forceRefresh: Boolean = false) {
        viewModelScope.launch {
            _transactionListState.value = TransactionListState.Loading
            
            when (val result = userRepository.getTransactions(userId)) {
                is NetworkResult.Success -> {
                    _transactionListState.value = TransactionListState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _transactionListState.value = TransactionListState.Error(
                        result.exception.message ?: "加载交易历史失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
