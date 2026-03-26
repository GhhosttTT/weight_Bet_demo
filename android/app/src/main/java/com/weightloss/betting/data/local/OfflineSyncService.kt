package com.weightloss.betting.data.local

import android.content.Context
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import com.weightloss.betting.data.local.dao.OfflineCheckInDao
import com.weightloss.betting.data.local.entity.OfflineCheckInEntity
import com.weightloss.betting.data.repository.CheckInData
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.CheckInRepository
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch
import java.util.Date
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 离线同步服务
 * 负责管理离线打卡队列和网络恢复时的自动同步
 */
@Singleton
class OfflineSyncService @Inject constructor(
    @ApplicationContext private val context: Context,
    private val offlineCheckInDao: OfflineCheckInDao,
    private val checkInRepository: CheckInRepository,
    private val cacheManager: CacheManager
) {
    
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    
    private val networkCallback = object : ConnectivityManager.NetworkCallback() {
        override fun onAvailable(network: Network) {
            // 网络恢复时自动同步
            scope.launch {
                syncPendingCheckIns()
            }
        }
    }
    
    init {
        // 注册网络状态监听
        val networkRequest = NetworkRequest.Builder()
            .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            .build()
        connectivityManager.registerNetworkCallback(networkRequest, networkCallback)
    }
    
    /**
     * 检查网络连接状态
     */
    fun isNetworkAvailable(): Boolean {
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
    
    /**
     * 添加离线打卡到队列
     */
    suspend fun addOfflineCheckIn(
        userId: String,
        planId: String,
        weight: Double,
        checkInDate: Date,
        photoUrl: String?,
        note: String?
    ): Long {
        val offlineCheckIn = OfflineCheckInEntity(
            userId = userId,
            planId = planId,
            weight = weight,
            checkInDate = checkInDate,
            photoUrl = photoUrl,
            note = note,
            createdAt = Date(),
            syncStatus = "pending",
            syncAttempts = 0
        )
        return offlineCheckInDao.insertOfflineCheckIn(offlineCheckIn)
    }
    
    /**
     * 观察待同步的打卡数量
     */
    fun observePendingCount(): Flow<Int> {
        return offlineCheckInDao.observePendingCount()
    }
    
    /**
     * 同步所有待同步的打卡记录
     */
    suspend fun syncPendingCheckIns(): SyncResult {
        if (!isNetworkAvailable()) {
            return SyncResult(
                success = false,
                syncedCount = 0,
                failedCount = 0,
                message = "网络不可用"
            )
        }
        
        val pendingCheckIns = offlineCheckInDao.getPendingCheckIns()
        var syncedCount = 0
        var failedCount = 0
        
        for (offlineCheckIn in pendingCheckIns) {
            // 更新同步状态为 syncing
            offlineCheckInDao.updateOfflineCheckIn(
                offlineCheckIn.copy(
                    syncStatus = "syncing",
                    lastSyncAttempt = Date()
                )
            )
            
            // 尝试同步
            val checkInData = CheckInData(
                userId = offlineCheckIn.userId,
                planId = offlineCheckIn.planId,
                weight = offlineCheckIn.weight,
                checkInDate = offlineCheckIn.checkInDate,
                photoUrl = offlineCheckIn.photoUrl,
                note = offlineCheckIn.note
            )
            
            when (val result = checkInRepository.createCheckIn(checkInData)) {
                is NetworkResult.Success -> {
                    // 同步成功
                    offlineCheckInDao.updateOfflineCheckIn(
                        offlineCheckIn.copy(
                            syncStatus = "synced",
                            lastSyncAttempt = Date()
                        )
                    )
                    
                    // 缓存同步后的打卡记录
                    cacheManager.cacheCheckIn(result.data)
                    
                    syncedCount++
                }
                is NetworkResult.Error -> {
                    // 同步失败
                    val newAttempts = offlineCheckIn.syncAttempts + 1
                    val newStatus = if (newAttempts >= 3) "failed" else "pending"
                    
                    offlineCheckInDao.updateOfflineCheckIn(
                        offlineCheckIn.copy(
                            syncStatus = newStatus,
                            syncAttempts = newAttempts,
                            lastSyncAttempt = Date(),
                            errorMessage = result.exception.message
                        )
                    )
                    
                    failedCount++
                }
                is NetworkResult.Loading -> {
                    // 不应该发生
                }
            }
        }
        
        // 清理已同步的记录
        offlineCheckInDao.deleteSyncedCheckIns()
        
        return SyncResult(
            success = failedCount == 0,
            syncedCount = syncedCount,
            failedCount = failedCount,
            message = if (failedCount == 0) {
                "同步成功: $syncedCount 条记录"
            } else {
                "同步完成: $syncedCount 条成功, $failedCount 条失败"
            }
        )
    }
    
    /**
     * 手动触发同步
     */
    suspend fun manualSync(): SyncResult {
        return syncPendingCheckIns()
    }
    
    /**
     * 获取用户的离线打卡记录
     */
    fun getOfflineCheckIns(userId: String): Flow<List<OfflineCheckInEntity>> {
        return offlineCheckInDao.getOfflineCheckInsByUser(userId)
    }
    
    /**
     * 清除所有离线记录
     */
    suspend fun clearOfflineQueue() {
        offlineCheckInDao.deleteAll()
    }
    
    /**
     * 释放资源
     */
    fun release() {
        connectivityManager.unregisterNetworkCallback(networkCallback)
    }
}

/**
 * 同步结果
 */
data class SyncResult(
    val success: Boolean,
    val syncedCount: Int,
    val failedCount: Int,
    val message: String
)
