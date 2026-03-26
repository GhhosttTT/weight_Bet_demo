package com.weightloss.betting.data.remote

import com.weightloss.betting.data.model.*
import retrofit2.Response
import retrofit2.http.*

/**
 * API 服务接口定义
 */
interface ApiService {
    
    // ==================== 认证 API ====================
    
    @POST("api/auth/register")
    suspend fun register(@Body request: RegisterRequest): Response<AuthResult>
    
    @POST("api/auth/login")
    suspend fun login(@Body request: LoginRequest): Response<AuthResult>
    
    @GET("api/me/pending-actions")
    suspend fun getPendingActions(): Response<PendingActionsResponse>
    
    @POST("api/auth/refresh")
    suspend fun refreshToken(@Body request: RefreshTokenRequest): Response<AuthResult>
    
    @POST("api/auth/google")
    suspend fun googleLogin(@Body request: GoogleLoginRequest): Response<AuthResult>
    
    // ==================== 用户 API ====================
    
    @GET("api/users/{userId}")
    suspend fun getUserProfile(@Path("userId") userId: String): Response<User>
    
    @PUT("api/users/{userId}")
    suspend fun updateUserProfile(
        @Path("userId") userId: String,
        @Body request: UpdateUserRequest
    ): Response<User>
    
    @GET("api/users/{userId}/balance")
    suspend fun getBalance(@Path("userId") userId: String): Response<Balance>
    
    @GET("api/users/{userId}/transactions")
    suspend fun getTransactions(
        @Path("userId") userId: String,
        @Query("page") page: Int = 1,
        @Query("limit") limit: Int = 20
    ): Response<List<Transaction>>
    
    // ==================== 对赌计划 API ====================
    
    @POST("api/betting-plans")
    suspend fun createPlan(@Body request: CreatePlanRequest): Response<BettingPlan>
    
    @GET("api/betting-plans/{planId}")
    suspend fun getPlanDetails(@Path("planId") planId: String): Response<BettingPlan>
    
    @GET("api/betting-plans/users/{userId}/plans")
    suspend fun getUserPlans(
        @Path("userId") userId: String,
        @Query("status") status: String? = null
    ): Response<List<BettingPlan>>
    
    @GET("api/betting-plans/users/{userId}/statistics")
    suspend fun getUserStatistics(@Path("userId") userId: String): Response<UserStatistics>
    
    @POST("api/betting-plans/{planId}/accept")
    suspend fun acceptPlan(
        @Path("planId") planId: String,
        @Body request: AcceptPlanRequest
    ): Response<BettingPlan>
    
    @POST("api/betting-plans/{planId}/reject")
    suspend fun rejectPlan(@Path("planId") planId: String): Response<Unit>
    
    @POST("api/betting-plans/{planId}/cancel")
    suspend fun cancelPlan(@Path("planId") planId: String): Response<Unit>
    
    @POST("api/betting-plans/{planId}/revoke")
    suspend fun revokePlan(@Path("planId") planId: String): Response<Unit>
    
    @POST("api/betting-plans/{planId}/confirm")
    suspend fun confirmPlan(@Path("planId") planId: String): Response<BettingPlan>
    
    // ==================== 打卡 API ====================
    
    @POST("api/check-ins")
    suspend fun createCheckIn(@Body request: CreateCheckInRequest): Response<CheckIn>
    
    @GET("api/betting-plans/{planId}/check-ins")
    suspend fun getCheckInHistory(
        @Path("planId") planId: String,
        @Query("user_id") userId: String? = null
    ): Response<List<CheckIn>>
    
    @GET("api/betting-plans/{planId}/progress")
    suspend fun getProgress(
        @Path("planId") planId: String,
        @Query("user_id") userId: String
    ): Response<ProgressStats>
    
    // ==================== 支付 API ====================
    
    @POST("api/payments/charge")
    suspend fun charge(@Body request: ChargeRequest): Response<ChargeResult>
    
    @POST("api/payments/withdraw")
    suspend fun withdraw(@Body request: WithdrawRequest): Response<WithdrawResult>
    
    // ==================== 社交 API ====================
    
    @GET("api/social/leaderboard/{type}")
    suspend fun getLeaderboard(
        @Path("type") type: String,
        @Query("limit") limit: Int = 100
    ): Response<List<LeaderboardEntry>>
    
    @POST("api/social/betting-plans/{planId}/comments")
    suspend fun postComment(
        @Path("planId") planId: String,
        @Body request: CommentRequest
    ): Response<Comment>
    
    @GET("api/social/betting-plans/{planId}/comments")
    suspend fun getComments(@Path("planId") planId: String): Response<List<Comment>>
    
    @GET("api/social/users/{userId}/badges")
    suspend fun getUserBadges(@Path("userId") userId: String): Response<List<Badge>>
    
    // ==================== 通知 API ====================
    
    @POST("api/notifications/register")
    suspend fun registerDeviceToken(@Body request: Map<String, String>): Response<Unit>
    
    // ==================== 邀请相关 API ====================
    
    @GET("api/users/search")
    suspend fun searchFriend(@Query("email") email: String): Response<UserSearchResult>
    
    @POST("api/betting-plans/{planId}/invite")
    suspend fun inviteFriend(
        @Path("planId") planId: String,
        @Body request: InviteFriendRequest
    ): Response<Invitation>
    
    @GET("api/invitations")
    suspend fun getInvitations(@Query("status") status: String? = null): Response<List<Invitation>>
    
    @GET("api/invitations/{invitationId}")
    suspend fun getInvitationDetails(@Path("invitationId") invitationId: String): Response<Invitation>
    
    @POST("api/invitations/{invitationId}/view")
    suspend fun markInvitationViewed(@Path("invitationId") invitationId: String): Response<Invitation>
    
    @POST("api/betting-plans/{planId}/abandon")
    suspend fun abandonPlan(
        @Path("planId") planId: String,
        @Body request: AbandonPlanRequest
    ): Response<AbandonPlanResult>
}
