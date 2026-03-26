package com.weightloss.betting.data.local

import com.weightloss.betting.data.local.dao.BettingPlanDao
import com.weightloss.betting.data.local.dao.CheckInDao
import com.weightloss.betting.data.local.dao.UserDao
import com.weightloss.betting.data.local.entity.BettingPlanEntity
import com.weightloss.betting.data.local.entity.CheckInEntity
import com.weightloss.betting.data.local.entity.UserEntity
import com.weightloss.betting.data.model.*
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.util.Date
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 本地缓存管理器
 * 负责管理用户信息、对赌计划和打卡历史的本地缓存
 */
@Singleton
class CacheManager @Inject constructor(
    private val userDao: UserDao,
    private val bettingPlanDao: BettingPlanDao,
    private val checkInDao: CheckInDao
) {
    
    // ==================== 用户缓存 ====================
    
    /**
     * 缓存用户信息
     */
    suspend fun cacheUser(user: User) {
        val entity = UserEntity(
            id = user.id,
            email = user.email,
            nickname = user.nickname,
            gender = user.gender,
            age = user.age,
            height = user.height,
            currentWeight = user.currentWeight,
            targetWeight = user.targetWeight,
            createdAt = user.createdAt,
            updatedAt = user.updatedAt
        )
        userDao.insertUser(entity)
    }
    
    /**
     * 获取缓存的用户信息
     */
    fun getCachedUser(userId: String): Flow<User?> {
        return userDao.getUserById(userId).map { entity ->
            entity?.let {
                User(
                    id = it.id,
                    email = it.email,
                    nickname = it.nickname,
                    gender = it.gender,
                    age = it.age,
                    height = it.height,
                    currentWeight = it.currentWeight,
                    targetWeight = it.targetWeight,
                    paymentMethodId = null, // 缓存中不存储支付方式ID
                    createdAt = it.createdAt,
                    updatedAt = it.updatedAt
                )
            }
        }
    }
    
    /**
     * 清除用户缓存
     */
    suspend fun clearUserCache() {
        userDao.deleteAll()
    }
    
    // ==================== 对赌计划缓存 ====================
    
    /**
     * 缓存对赌计划
     */
    suspend fun cachePlan(plan: BettingPlan) {
        val entity = BettingPlanEntity(
            id = plan.id,
            creatorId = plan.creatorId,
            participantId = plan.participantId,
            status = plan.status,
            betAmount = plan.betAmount,
            startDate = plan.startDate,
            endDate = plan.endDate,
            description = plan.description,
            creatorInitialWeight = plan.creatorInitialWeight,
            creatorTargetWeight = plan.creatorTargetWeight,
            participantInitialWeight = plan.participantInitialWeight,
            participantTargetWeight = plan.participantTargetWeight,
            createdAt = plan.createdAt,
            activatedAt = plan.activatedAt
        )
        bettingPlanDao.insertPlan(entity)
    }
    
    /**
     * 批量缓存对赌计划
     */
    suspend fun cachePlans(plans: List<BettingPlan>) {
        val entities = plans.map { plan ->
            BettingPlanEntity(
                id = plan.id,
                creatorId = plan.creatorId,
                participantId = plan.participantId,
                status = plan.status,
                betAmount = plan.betAmount,
                startDate = plan.startDate,
                endDate = plan.endDate,
                description = plan.description,
                creatorInitialWeight = plan.creatorInitialWeight,
                creatorTargetWeight = plan.creatorTargetWeight,
                participantInitialWeight = plan.participantInitialWeight,
                participantTargetWeight = plan.participantTargetWeight,
                createdAt = plan.createdAt,
                activatedAt = plan.activatedAt
            )
        }
        bettingPlanDao.insertPlans(entities)
    }
    
    /**
     * 获取缓存的对赌计划
     */
    fun getCachedPlan(planId: String): Flow<BettingPlan?> {
        return bettingPlanDao.getPlanById(planId).map { entity ->
            entity?.let { entityToPlan(it) }
        }
    }
    
    /**
     * 获取用户的所有缓存计划
     */
    fun getCachedUserPlans(userId: String): Flow<List<BettingPlan>> {
        return bettingPlanDao.getUserPlans(userId).map { entities ->
            entities.map { entityToPlan(it) }
        }
    }
    
    /**
     * 获取用户指定状态的缓存计划
     */
    fun getCachedUserPlansByStatus(userId: String, status: String): Flow<List<BettingPlan>> {
        return bettingPlanDao.getUserPlansByStatus(userId, status).map { entities ->
            entities.map { entityToPlan(it) }
        }
    }
    
    /**
     * 清除计划缓存
     */
    suspend fun clearPlanCache() {
        bettingPlanDao.deleteAll()
    }
    
    // ==================== 打卡历史缓存 ====================
    
    /**
     * 缓存打卡记录
     */
    suspend fun cacheCheckIn(checkIn: CheckIn) {
        val entity = CheckInEntity(
            id = checkIn.id,
            userId = checkIn.userId,
            planId = checkIn.planId,
            weight = checkIn.weight,
            checkInDate = checkIn.checkInDate,
            photoUrl = checkIn.photoUrl,
            note = checkIn.note,
            reviewStatus = checkIn.reviewStatus,
            createdAt = checkIn.createdAt
        )
        checkInDao.insertCheckIn(entity)
    }
    
    /**
     * 批量缓存打卡记录
     */
    suspend fun cacheCheckIns(checkIns: List<CheckIn>) {
        val entities = checkIns.map { checkIn ->
            CheckInEntity(
                id = checkIn.id,
                userId = checkIn.userId,
                planId = checkIn.planId,
                weight = checkIn.weight,
                checkInDate = checkIn.checkInDate,
                photoUrl = checkIn.photoUrl,
                note = checkIn.note,
                reviewStatus = checkIn.reviewStatus,
                createdAt = checkIn.createdAt
            )
        }
        checkInDao.insertCheckIns(entities)
    }
    
    /**
     * 获取计划的缓存打卡历史
     */
    fun getCachedCheckIns(planId: String): Flow<List<CheckIn>> {
        return checkInDao.getCheckInsByPlan(planId).map { entities ->
            entities.map { entityToCheckIn(it) }
        }
    }
    
    /**
     * 获取用户在计划中的缓存打卡历史
     */
    fun getCachedUserCheckIns(planId: String, userId: String): Flow<List<CheckIn>> {
        return checkInDao.getCheckInsByPlanAndUser(planId, userId).map { entities ->
            entities.map { entityToCheckIn(it) }
        }
    }
    
    /**
     * 清除打卡缓存
     */
    suspend fun clearCheckInCache() {
        checkInDao.deleteAll()
    }
    
    /**
     * 清除指定计划的打卡缓存
     */
    suspend fun clearCheckInCacheByPlan(planId: String) {
        checkInDao.deleteCheckInsByPlan(planId)
    }
    
    // ==================== 辅助方法 ====================
    
    private fun entityToPlan(entity: BettingPlanEntity): BettingPlan {
        return BettingPlan(
            id = entity.id,
            creatorId = entity.creatorId,
            creatorNickname = null, // 本地缓存不存储用户信息
            creatorEmail = null, // 本地缓存不存储用户信息
            participantId = entity.participantId,
            participantNickname = null, // 本地缓存不存储用户信息
            participantEmail = null, // 本地缓存不存储用户信息
            status = entity.status,
            betAmount = entity.betAmount,
            startDate = entity.startDate,
            endDate = entity.endDate,
            description = entity.description,
            creatorInitialWeight = entity.creatorInitialWeight,
            creatorTargetWeight = entity.creatorTargetWeight,
            creatorTargetWeightLoss = null, // 本地缓存不存储计算字段
            participantInitialWeight = entity.participantInitialWeight,
            participantTargetWeight = entity.participantTargetWeight,
            participantTargetWeightLoss = null, // 本地缓存不存储计算字段
            createdAt = entity.createdAt,
            activatedAt = entity.activatedAt
        )
    }
    
    private fun entityToCheckIn(entity: CheckInEntity): CheckIn {
        return CheckIn(
            id = entity.id,
            userId = entity.userId,
            planId = entity.planId,
            weight = entity.weight,
            checkInDate = entity.checkInDate,
            photoUrl = entity.photoUrl,
            note = entity.note,
            reviewStatus = entity.reviewStatus,
            createdAt = entity.createdAt
        )
    }
}
