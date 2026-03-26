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
 * 对赌计划 Repository - 处理对赌计划相关的数据操作
 * 集成本地缓存策略
 */
@Singleton
class BettingPlanRepository @Inject constructor(
    private val apiService: ApiService,
    private val cacheManager: CacheManager
) : BaseRepository() {
    
    /**
     * 创建对赌计划
     */
    suspend fun createPlan(request: CreatePlanRequest): NetworkResult<BettingPlan> {
        return when (val result = safeApiCall { apiService.createPlan(request) }) {
            is NetworkResult.Success -> {
                // 缓存新创建的计划
                cacheManager.cachePlan(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 获取计划详情 (优先从缓存读取)
     */
    suspend fun getPlanDetails(planId: String, forceRefresh: Boolean = false): NetworkResult<BettingPlan> {
        // 如果不强制刷新,先尝试从缓存读取
        if (!forceRefresh) {
            val cachedPlan = cacheManager.getCachedPlan(planId).firstOrNull()
            if (cachedPlan != null) {
                return NetworkResult.Success(cachedPlan)
            }
        }
        
        // 从网络获取
        return when (val result = safeApiCall { apiService.getPlanDetails(planId) }) {
            is NetworkResult.Success -> {
                // 缓存计划
                cacheManager.cachePlan(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 观察缓存的计划详情
     */
    fun observeCachedPlan(planId: String): Flow<BettingPlan?> {
        return cacheManager.getCachedPlan(planId)
    }
    
    /**
     * 获取用户的所有计划 (优先从缓存读取)
     */
    suspend fun getUserPlans(
        userId: String,
        status: String? = null,
        forceRefresh: Boolean = false
    ): NetworkResult<List<BettingPlan>> {
        // 如果不强制刷新,先尝试从缓存读取
        if (!forceRefresh) {
            val cachedPlans = if (status != null) {
                cacheManager.getCachedUserPlansByStatus(userId, status).firstOrNull()
            } else {
                cacheManager.getCachedUserPlans(userId).firstOrNull()
            }
            
            if (cachedPlans != null && cachedPlans.isNotEmpty()) {
                return NetworkResult.Success(cachedPlans)
            }
        }
        
        // 从网络获取
        return when (val result = safeApiCall { apiService.getUserPlans(userId, status) }) {
            is NetworkResult.Success -> {
                // 缓存计划列表
                cacheManager.cachePlans(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 观察用户的缓存计划
     */
    fun observeCachedUserPlans(userId: String, status: String? = null): Flow<List<BettingPlan>> {
        return if (status != null) {
            cacheManager.getCachedUserPlansByStatus(userId, status)
        } else {
            cacheManager.getCachedUserPlans(userId)
        }
    }
    
    /**
     * 接受对赌计划
     */
    suspend fun acceptPlan(
        planId: String,
        request: AcceptPlanRequest
    ): NetworkResult<BettingPlan> {
        return when (val result = safeApiCall { apiService.acceptPlan(planId, request) }) {
            is NetworkResult.Success -> {
                // 更新缓存
                cacheManager.cachePlan(result.data)
                result
            }
            else -> result
        }
    }
    
    /**
     * 拒绝对赌计划
     */
    suspend fun rejectPlan(planId: String): NetworkResult<Unit> {
        return safeApiCall { apiService.rejectPlan(planId) }
    }
    
    /**
     * 取消对赌计划
     */
    suspend fun cancelPlan(planId: String): NetworkResult<Unit> {
        return safeApiCall { apiService.cancelPlan(planId) }
    }
    
    /**
     * 撤销对赌计划
     */
    suspend fun revokePlan(planId: String): NetworkResult<Unit> {
        return safeApiCall { apiService.revokePlan(planId) }
    }
    
    /**
     * 确认对赌计划生效
     */
    suspend fun confirmPlan(planId: String): NetworkResult<BettingPlan> {
        return safeApiCall { apiService.confirmPlan(planId) }
    }
    
    /**
     * 搜索好友 (通过邮箱)
     */
    suspend fun searchFriend(email: String): NetworkResult<UserSearchResult> {
        return safeApiCall { apiService.searchFriend(email) }
    }
    
    /**
     * 邀请好友参与计划
     */
    suspend fun inviteFriend(planId: String, inviteeEmail: String): NetworkResult<Invitation> {
        val request = InviteFriendRequest(inviteeEmail)
        return safeApiCall { apiService.inviteFriend(planId, request) }
    }
    
    /**
     * 获取用户的邀请列表
     */
    suspend fun getInvitations(status: String? = null): NetworkResult<List<Invitation>> {
        return safeApiCall { apiService.getInvitations(status) }
    }
    
    /**
     * 获取邀请详情
     */
    suspend fun getInvitationDetails(invitationId: String): NetworkResult<Invitation> {
        return safeApiCall { apiService.getInvitationDetails(invitationId) }
    }
    
    /**
     * 标记邀请为已查看
     */
    suspend fun markInvitationViewed(invitationId: String): NetworkResult<Invitation> {
        return safeApiCall { apiService.markInvitationViewed(invitationId) }
    }
    
    /**
     * 放弃计划
     */
    suspend fun abandonPlan(planId: String, confirmation: Boolean = true): NetworkResult<AbandonPlanResult> {
        val request = AbandonPlanRequest(confirmation)
        return safeApiCall { apiService.abandonPlan(planId, request) }
    }
    
    /**
     * 获取用户统计信息
     */
    suspend fun getUserStatistics(userId: String): NetworkResult<UserStatistics> {
        return safeApiCall { apiService.getUserStatistics(userId) }
    }
    
    /**
     * 清除计划缓存
     */
    suspend fun clearCache() {
        cacheManager.clearPlanCache()
    }
}
