package com.weightloss.betting.data.repository

import com.weightloss.betting.data.local.CacheManager
import com.weightloss.betting.data.model.*
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 用户 Repository - 处理用户信息相关的数据操作
 * 集成本地缓存策略
 */
@Singleton
class UserRepository @Inject constructor(
    private val apiService: ApiService,
    private val cacheManager: CacheManager
) : BaseRepository() {
    
    /**
     * 获取用户信息 (优先从缓存读取)
     */
    suspend fun getUserProfile(userId: String, forceRefresh: Boolean = false): NetworkResult<User> {
        // 如果不强制刷新,先尝试从缓存读取
        if (!forceRefresh) {
            val cachedUser = cacheManager.getCachedUser(userId).firstOrNull()
            if (cachedUser != null) {
                return NetworkResult.Success(cachedUser)
            }
        }
        
        // 从网络获取
        return when (val result = safeApiCall { apiService.getUserProfile(userId) }) {
            is NetworkResult.Success -> {
                // 缓存用户信息
                cacheManager.cacheUser(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 观察缓存的用户信息
     */
    fun observeCachedUser(userId: String): Flow<User?> {
        return cacheManager.getCachedUser(userId)
    }
    
    /**
     * 更新用户信息
     */
    suspend fun updateUserProfile(
        userId: String,
        request: UpdateUserRequest
    ): NetworkResult<User> {
        return when (val result = safeApiCall { apiService.updateUserProfile(userId, request) }) {
            is NetworkResult.Success -> {
                // 更新缓存
                cacheManager.cacheUser(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 获取账户余额
     */
    suspend fun getBalance(userId: String): NetworkResult<Balance> {
        return safeApiCall { apiService.getBalance(userId) }
    }
    
    /**
     * 获取交易历史
     */
    suspend fun getTransactions(
        userId: String,
        page: Int = 1,
        limit: Int = 20
    ): NetworkResult<List<Transaction>> {
        return safeApiCall { apiService.getTransactions(userId, page, limit) }
    }
    
    /**
     * 清除用户缓存
     */
    suspend fun clearCache() {
        cacheManager.clearUserCache()
    }
}
