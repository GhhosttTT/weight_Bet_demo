package com.weightloss.betting.data.local.dao

import androidx.room.*
import com.weightloss.betting.data.local.entity.OfflineCheckInEntity
import kotlinx.coroutines.flow.Flow

/**
 * 离线打卡队列 DAO
 */
@Dao
interface OfflineCheckInDao {
    
    /**
     * 获取所有待同步的打卡记录
     */
    @Query("SELECT * FROM offline_check_ins WHERE syncStatus = 'pending' OR syncStatus = 'failed' ORDER BY createdAt ASC")
    suspend fun getPendingCheckIns(): List<OfflineCheckInEntity>
    
    /**
     * 观察待同步的打卡记录数量
     */
    @Query("SELECT COUNT(*) FROM offline_check_ins WHERE syncStatus = 'pending' OR syncStatus = 'failed'")
    fun observePendingCount(): Flow<Int>
    
    /**
     * 插入离线打卡记录
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertOfflineCheckIn(checkIn: OfflineCheckInEntity): Long
    
    /**
     * 更新离线打卡记录
     */
    @Update
    suspend fun updateOfflineCheckIn(checkIn: OfflineCheckInEntity)
    
    /**
     * 删除已同步的打卡记录
     */
    @Query("DELETE FROM offline_check_ins WHERE syncStatus = 'synced'")
    suspend fun deleteSyncedCheckIns()
    
    /**
     * 删除指定的离线打卡记录
     */
    @Delete
    suspend fun deleteOfflineCheckIn(checkIn: OfflineCheckInEntity)
    
    /**
     * 删除所有离线打卡记录
     */
    @Query("DELETE FROM offline_check_ins")
    suspend fun deleteAll()
    
    /**
     * 获取指定用户的离线打卡记录
     */
    @Query("SELECT * FROM offline_check_ins WHERE userId = :userId ORDER BY createdAt DESC")
    fun getOfflineCheckInsByUser(userId: String): Flow<List<OfflineCheckInEntity>>
}
