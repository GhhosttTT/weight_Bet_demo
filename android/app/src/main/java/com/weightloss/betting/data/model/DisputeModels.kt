package com.weightloss.betting.data.model

import com.google.gson.annotations.SerializedName

data class DisputeCreateRequest(
    val reason: String,
    val description: String? = null
)

data class DisputeResponse(
    val id: String,
    @SerializedName("settlement_id") val settlementId: String,
    val status: String,
    @SerializedName("admin_notes") val adminNotes: String? = null
)
