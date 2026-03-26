package com.weightloss.betting.data.model

import com.google.gson.annotations.SerializedName
import java.util.Date

// ==================== 认证相关 ====================

data class RegisterRequest(
    val email: String,
    val password: String,
    val nickname: String,
    val gender: String,
    val age: Int,
    val height: Double,
    @SerializedName("current_weight")
    val currentWeight: Double
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class RefreshTokenRequest(
    val refreshToken: String
)

data class GoogleLoginRequest(
    val idToken: String
)

data class AuthResult(
    @SerializedName("user_id")
    val userId: String,
    val email: String,
    val nickname: String,
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("refresh_token")
    val refreshToken: String
)

// ==================== 用户相关 ====================

data class User(
    val id: String,
    val email: String,
    val nickname: String,
    val gender: String,
    val age: Int,
    val height: Double,
    @SerializedName("current_weight")
    val currentWeight: Double,
    @SerializedName("target_weight")
    val targetWeight: Double?,
    @SerializedName("payment_method_id")
    val paymentMethodId: String?,
    @SerializedName("created_at")
    val createdAt: Date,
    @SerializedName("updated_at")
    val updatedAt: Date
)

data class UpdateUserRequest(
    val nickname: String?,
    val gender: String?,
    val age: Int?,
    val height: Double?,
    @SerializedName("current_weight")
    val currentWeight: Double?,
    @SerializedName("target_weight")
    val targetWeight: Double?
)

data class Balance(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("available_balance")
    val availableBalance: Double,
    @SerializedName("frozen_balance")
    val frozenBalance: Double,
    @SerializedName("updated_at")
    val updatedAt: Date
)

data class Transaction(
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    val type: String,
    val amount: Double,
    val status: String,
    @SerializedName("created_at")
    val createdAt: Date
)

// ==================== 对赌计划相关 ====================

data class BettingPlan(
    val id: String,
    @SerializedName("creator_id")
    val creatorId: String,
    @SerializedName("creator_nickname")
    val creatorNickname: String?,
    @SerializedName("creator_email")
    val creatorEmail: String?,
    @SerializedName("participant_id")
    val participantId: String?,
    @SerializedName("participant_nickname")
    val participantNickname: String?,
    @SerializedName("participant_email")
    val participantEmail: String?,
    val status: String,
    @SerializedName("bet_amount")
    val betAmount: Double,
    @SerializedName("start_date")
    val startDate: Date,
    @SerializedName("end_date")
    val endDate: Date,
    val description: String?,
    @SerializedName("creator_initial_weight")
    val creatorInitialWeight: Double,
    @SerializedName("creator_target_weight")
    val creatorTargetWeight: Double,
    @SerializedName("creator_target_weight_loss")
    val creatorTargetWeightLoss: Double?,
    @SerializedName("participant_initial_weight")
    val participantInitialWeight: Double?,
    @SerializedName("participant_target_weight")
    val participantTargetWeight: Double?,
    @SerializedName("participant_target_weight_loss")
    val participantTargetWeightLoss: Double?,
    @SerializedName("created_at")
    val createdAt: Date,
    @SerializedName("activated_at")
    val activatedAt: Date?
)

data class CreatePlanRequest(
    @SerializedName("bet_amount")
    val betAmount: Double,
    @SerializedName("start_date")
    val startDate: String,
    @SerializedName("end_date")
    val endDate: String,
    @SerializedName("initial_weight")
    val initialWeight: Double,
    @SerializedName("target_weight")
    val targetWeight: Double,
    val description: String?
)

data class AcceptPlanRequest(
    @SerializedName("initial_weight")
    val initialWeight: Double,
    @SerializedName("target_weight")
    val targetWeight: Double
)

// ==================== 打卡相关 ====================

data class CheckIn(
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("plan_id")
    val planId: String,
    val weight: Double,
    @SerializedName("check_in_date")
    val checkInDate: Date,
    @SerializedName("photo_url")
    val photoUrl: String?,
    val note: String?,
    @SerializedName("review_status")
    val reviewStatus: String,
    @SerializedName("created_at")
    val createdAt: Date
)

data class CreateCheckInRequest(
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("plan_id")
    val planId: String,
    val weight: Double,
    @SerializedName("check_in_date")
    val checkInDate: String,
    val note: String?
)

data class ProgressStats(
    @SerializedName("current_weight")
    val currentWeight: Double,
    @SerializedName("initial_weight")
    val initialWeight: Double,
    @SerializedName("target_weight")
    val targetWeight: Double,
    @SerializedName("weight_loss")
    val weightLoss: Double,
    @SerializedName("target_weight_loss")
    val targetWeightLoss: Double,
    @SerializedName("progress_percentage")
    val progressPercentage: Double,
    @SerializedName("check_in_count")
    val checkInCount: Int,
    @SerializedName("days_remaining")
    val daysRemaining: Int
)

// ==================== 支付相关 ====================

data class ChargeRequest(
    val amount: Double,
    @SerializedName("payment_method_id")
    val paymentMethodId: String
)

data class ChargeResult(
    val success: Boolean,
    val transactionId: String?,
    val message: String?
)

data class WithdrawRequest(
    val userId: String,
    val amount: Double
)

data class WithdrawResult(
    val success: Boolean,
    val transactionId: String?,
    val message: String?
)

// ==================== 社交相关 ====================

data class LeaderboardEntry(
    @SerializedName("user_id")
    val userId: String,
    val nickname: String,
    val value: Double,
    val rank: Int
)

data class CommentRequest(
    val userId: String,
    val content: String
)

data class Comment(
    val id: String,
    @SerializedName("user_id")
    val userId: String,
    @SerializedName("plan_id")
    val planId: String,
    val content: String,
    @SerializedName("created_at")
    val createdAt: Date
)

data class Badge(
    val id: String,
    val name: String,
    val description: String,
    @SerializedName("icon_url")
    val iconUrl: String?,
    @SerializedName("awarded_at")
    val awardedAt: Date
)

// ==================== 邀请相关 ====================

data class UserSearchResult(
    @SerializedName("user_id")
    val userId: String,
    val nickname: String,
    val age: Int,
    val gender: String
)

data class Invitation(
    val id: String,
    @SerializedName("plan_id")
    val planId: String,
    @SerializedName("inviter_id")
    val inviterId: String,
    @SerializedName("inviter_name")
    val inviterName: String,
    @SerializedName("invitee_email")
    val inviteeEmail: String,
    @SerializedName("invitee_id")
    val inviteeId: String?,
    val status: String,
    @SerializedName("sent_at")
    val sentAt: Date,
    @SerializedName("viewed_at")
    val viewedAt: Date?,
    @SerializedName("responded_at")
    val respondedAt: Date?
)

data class InviteFriendRequest(
    @SerializedName("invitee_email")
    val inviteeEmail: String
)

data class AbandonPlanRequest(
    val confirmation: Boolean
)

data class AbandonPlanResult(
    val success: Boolean,
    @SerializedName("plan_id")
    val planId: String,
    val status: String,
    @SerializedName("refunded_amount")
    val refundedAmount: Double?,
    @SerializedName("transferred_amount")
    val transferredAmount: Double?,
    val message: String
)

data class UserStatistics(
    @SerializedName("active_plans_count")
    val activePlansCount: Int,
    @SerializedName("pending_plans_count")
    val pendingPlansCount: Int,
    @SerializedName("waiting_double_check_count")
    val waitingDoubleCheckCount: Int,
    @SerializedName("completed_plans_count")
    val completedPlansCount: Int,
    @SerializedName("total_check_in_days")
    val totalCheckInDays: Int
)
