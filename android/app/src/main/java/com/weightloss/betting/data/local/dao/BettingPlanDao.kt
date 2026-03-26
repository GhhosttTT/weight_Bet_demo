package com.weightloss.betting.data.local.dao

import androidx.room.*
import com.weightloss.betting.data.local.entity.BettingPlanEntity
import kotlinx.coroutines.flow.Flow

/**
 * 对赌计划 DAO
 */
@Dao
interface BettingPlanDao {
    
    @Query("SELECT * FROM betting_plans WHERE id = :planId")
    fun getPlanById(planId: String): Flow<BettingPlanEntity?>
    
    @Query("SELECT * FROM betting_plans WHERE creatorId = :userId OR participantId = :userId ORDER BY createdAt DESC")
    fun getUserPlans(userId: String): Flow<List<BettingPlanEntity>>
    
    @Query("SELECT * FROM betting_plans WHERE (creatorId = :userId OR participantId = :userId) AND status = :status ORDER BY createdAt DESC")
    fun getUserPlansByStatus(userId: String, status: String): Flow<List<BettingPlanEntity>>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPlan(plan: BettingPlanEntity)
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertPlans(plans: List<BettingPlanEntity>)
    
    @Update
    suspend fun updatePlan(plan: BettingPlanEntity)
    
    @Delete
    suspend fun deletePlan(plan: BettingPlanEntity)
    
    @Query("DELETE FROM betting_plans")
    suspend fun deleteAll()
}
