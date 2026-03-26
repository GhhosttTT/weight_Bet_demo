package com.weightloss.betting.data.local.dao

import androidx.room.*
import com.weightloss.betting.data.local.entity.CheckInEntity
import kotlinx.coroutines.flow.Flow

/**
 * 打卡记录 DAO
 */
@Dao
interface CheckInDao {
    
    @Query("SELECT * FROM check_ins WHERE planId = :planId ORDER BY checkInDate DESC")
    fun getCheckInsByPlan(planId: String): Flow<List<CheckInEntity>>
    
    @Query("SELECT * FROM check_ins WHERE planId = :planId AND userId = :userId ORDER BY checkInDate DESC")
    fun getCheckInsByPlanAndUser(planId: String, userId: String): Flow<List<CheckInEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCheckIn(checkIn: CheckInEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertCheckIns(checkIns: List<CheckInEntity>)
    
    @Delete
    suspend fun deleteCheckIn(checkIn: CheckInEntity)
    
    @Query("DELETE FROM check_ins WHERE planId = :planId")
    suspend fun deleteCheckInsByPlan(planId: String)
    
    @Query("DELETE FROM check_ins")
    suspend fun deleteAll()
}
