package com.weightloss.betting.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

/**
 * 打卡记录本地实体
 */
@Entity(tableName = "check_ins")
data class CheckInEntity(
    @PrimaryKey
    val id: String,
    val userId: String,
    val planId: String,
    val weight: Double,
    val checkInDate: Date,
    val photoUrl: String?,
    val note: String?,
    val reviewStatus: String,
    val createdAt: Date
)
