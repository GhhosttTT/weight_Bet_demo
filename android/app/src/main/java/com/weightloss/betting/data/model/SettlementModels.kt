package com.weightloss.betting.data.model

import com.google.gson.annotations.SerializedName

data class SettlementChoiceRequest(
    @SerializedName("self_achieved") val selfAchieved: Boolean,
    @SerializedName("opponent_achieved") val opponentAchieved: Boolean
)

data class SettlementChoiceResponse(
    @SerializedName("id") val id: String,
    @SerializedName("plan_id") val planId: String,
    @SerializedName("user_id") val userId: String,
    @SerializedName("self_achieved") val selfAchieved: Boolean,
    @SerializedName("opponent_achieved") val opponentAchieved: Boolean,
    @SerializedName("round") val round: Int
)

data class SettlementSelectionStatus(
    @SerializedName("plan_id") val planId: String,
    @SerializedName("current_round") val currentRound: Int,
    @SerializedName("creator_submitted") val creatorSubmitted: Boolean,
    @SerializedName("participant_submitted") val participantSubmitted: Boolean,
    @SerializedName("current_user_submitted") val currentUserSubmitted: Boolean,
    @SerializedName("matched") val matched: Boolean = false,
    @SerializedName("settlement_completed") val settlementCompleted: Boolean,
    @SerializedName("in_arbitration") val inArbitration: Boolean
)
