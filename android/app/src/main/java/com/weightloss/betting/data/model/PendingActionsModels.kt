package com.weightloss.betting.data.model

import com.google.gson.annotations.SerializedName

/**
 * Pending Actions Response
 */
data class PendingActionsResponse(
    @SerializedName("invitations")
    val invitations: List<InvitationItem> = emptyList(),
    
    @SerializedName("doubleChecks")
    val doubleChecks: List<DoubleCheckItem> = emptyList()
)

/**
 * Invitation Item
 */
data class InvitationItem(
    @SerializedName("id")
    val id: String,
    
    @SerializedName("planId")
    val planId: String,
    
    @SerializedName("fromUserId")
    val fromUserId: String,
    
    @SerializedName("message")
    val message: String?,
    
    @SerializedName("type")
    val type: String,
    
    @SerializedName("isFirstTime")
    val isFirstTime: Boolean
)

/**
 * Double Check Item
 */
data class DoubleCheckItem(
    @SerializedName("planId")
    val planId: String,
    
    @SerializedName("initiatorId")
    val initiatorId: String,
    
    @SerializedName("reason")
    val reason: String,
    
    @SerializedName("isPending")
    val isPending: Boolean
)
