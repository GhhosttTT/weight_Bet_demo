package com.weightloss.betting.data.repository

import com.weightloss.betting.data.model.*
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 支付 Repository - 处理支付相关的数据操作
 */
@Singleton
class PaymentRepository @Inject constructor(
    private val apiService: ApiService
) : BaseRepository() {
    
    /**
     * 充值
     */
    suspend fun charge(request: ChargeRequest): NetworkResult<ChargeResult> {
        return safeApiCall { apiService.charge(request) }
    }
    
    /**
     * 提现
     */
    suspend fun withdraw(request: WithdrawRequest): NetworkResult<WithdrawResult> {
        return safeApiCall { apiService.withdraw(request) }
    }
}
