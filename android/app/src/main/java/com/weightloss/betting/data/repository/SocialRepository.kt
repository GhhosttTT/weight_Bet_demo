package com.weightloss.betting.data.repository

import com.weightloss.betting.data.model.*
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 社交 Repository - 处理社交功能相关的数据操作
 */
@Singleton
class SocialRepository @Inject constructor(
    private val apiService: ApiService
) : BaseRepository() {
    
    /**
     * 获取排行榜
     * @param type 排行榜类型: weight-loss, check-in-streak, win-rate
     */
    suspend fun getLeaderboard(
        type: String,
        limit: Int = 100
    ): NetworkResult<List<LeaderboardEntry>> {
        return safeApiCall { apiService.getLeaderboard(type, limit) }
    }
    
    /**
     * 发表评论
     */
    suspend fun postComment(
        planId: String,
        request: CommentRequest
    ): NetworkResult<Comment> {
        return safeApiCall { apiService.postComment(planId, request) }
    }
    
    /**
     * 获取评论列表
     */
    suspend fun getComments(planId: String): NetworkResult<List<Comment>> {
        return safeApiCall { apiService.getComments(planId) }
    }
    
    /**
     * 获取用户勋章
     */
    suspend fun getUserBadges(userId: String): NetworkResult<List<Badge>> {
        return safeApiCall { apiService.getUserBadges(userId) }
    }
}
