package com.weightloss.betting.data.repository

import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 通知 Repository - 处理通知相关的数据操作
 */
@Singleton
class NotificationRepository @Inject constructor(
    private val apiService: ApiService
) : BaseRepository() {
    
    /**
     * 注册设备令牌
     */
    suspend fun registerDeviceToken(token: String): NetworkResult<Unit> {
        return safeApiCall {
            apiService.registerDeviceToken(mapOf("token" to token, "platform" to "android"))
        }
    }
}
