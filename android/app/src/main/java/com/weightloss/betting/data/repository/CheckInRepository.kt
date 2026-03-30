package com.weightloss.betting.data.repository

import com.weightloss.betting.data.local.CacheManager
import com.weightloss.betting.data.local.OfflineSyncService
import com.weightloss.betting.data.model.*
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.firstOrNull
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 打卡 Repository - 处理打卡相关的数据操作
 * 集成本地缓存和离线支持
 */
@Singleton
class CheckInRepository @Inject constructor(
    private val apiService: ApiService,
    private val cacheManager: CacheManager
) : BaseRepository() {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.CHINA)
    
    private fun formatToString(date: Date): String {
        return dateFormat.format(date)
    }
    
    /**
     * 创建打卡记录 (支持离线)
     */
    suspend fun createCheckIn(data: CheckInData): NetworkResult<CheckIn> {
        // TODO: Implement offline support without circular dependency
        // For now, only online mode is supported
            
        val request = CreateCheckInRequest(
            planId = data.planId,
            weight = data.weight,
            checkInDate = formatToString(data.checkInDate),
            note = data.note
        )
        
        return when (val result = safeApiCall { apiService.createCheckIn(request) }) {
            is NetworkResult.Success -> {
                // 缓存打卡记录
                cacheManager.cacheCheckIn(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 获取打卡历史 (优先从缓存读取)
     */
    suspend fun getCheckInHistory(
        planId: String,
        userId: String? = null,
        forceRefresh: Boolean = false
    ): NetworkResult<List<CheckIn>> {
        // 如果不强制刷新,先尝试从缓存读取
        if (!forceRefresh) {
            val cachedCheckIns = if (userId != null) {
                cacheManager.getCachedUserCheckIns(planId, userId).firstOrNull()
            } else {
                cacheManager.getCachedCheckIns(planId).firstOrNull()
            }
            
            if (cachedCheckIns != null && cachedCheckIns.isNotEmpty()) {
                return NetworkResult.Success(cachedCheckIns)
            }
        }
        
        // 从网络获取
        return when (val result = safeApiCall { apiService.getCheckInHistory(planId, userId) }) {
            is NetworkResult.Success -> {
                // 缓存打卡历史
                cacheManager.cacheCheckIns(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 观察缓存的打卡历史
     */
    fun observeCachedCheckIns(planId: String, userId: String? = null): Flow<List<CheckIn>> {
        return if (userId != null) {
            cacheManager.getCachedUserCheckIns(planId, userId)
        } else {
            cacheManager.getCachedCheckIns(planId)
        }
    }
    
    /**
     * 获取进度统计
     */
    suspend fun getProgress(
        planId: String,
        userId: String
    ): NetworkResult<ProgressStats> {
        return safeApiCall { apiService.getProgress(planId, userId) }
    }
    
    fun observePendingSyncCount(): Flow<Int> {
        // TODO: Implement without circular dependency
        return kotlinx.coroutines.flow.flowOf(0)
    }
    
    /**
     * 手动触发同步
     */
    suspend fun syncOfflineCheckIns() {
        // TODO: Implement without circular dependency
    }
    
    /**
     * 清除打卡缓存
     */
    suspend fun clearCache(planId: String? = null) {
        if (planId != null) {
            cacheManager.clearCheckInCacheByPlan(planId)
        } else {
            cacheManager.clearCheckInCache()
        }
    }
}

/**
 * 打卡数据 (用于创建打卡)
 */
data class CheckInData(
    val userId: String,
    val planId: String,
    val weight: Double,
    val checkInDate: java.util.Date,
    val photoUrl: String? = null,
    val note: String? = null
)
