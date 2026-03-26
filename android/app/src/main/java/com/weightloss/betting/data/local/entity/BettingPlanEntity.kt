package com.weightloss.betting.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

/**
 * 对赌计划本地实体
 */
@Entity(tableName = "betting_plans")
data class BettingPlanEntity(
    @PrimaryKey
    val id: String,
    val creatorId: String,
    val participantId: String?,
    val status: String,
    val betAmount: Double,
    val startDate: Date,
    val endDate: Date,
    val description: String?,
    val creatorInitialWeight: Double,
    val creatorTargetWeight: Double,
    val participantInitialWeight: Double?,
    val participantTargetWeight: Double?,
    val createdAt: Date,
    val activatedAt: Date?
)
