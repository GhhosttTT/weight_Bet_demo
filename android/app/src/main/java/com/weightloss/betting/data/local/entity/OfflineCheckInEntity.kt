package com.weightloss.betting.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

/**
 * 离线打卡队列实体
 * 用于存储离线状态下创建的打卡记录
 */
@Entity(tableName = "offline_check_ins")
data class OfflineCheckInEntity(
    @PrimaryKey(autoGenerate = true)
    val localId: Long = 0,
    val userId: String,
    val planId: String,
    val weight: Double,
    val checkInDate: Date,
    val photoUrl: String?,
    val note: String?,
    val createdAt: Date,
    val syncStatus: String, // pending, syncing, synced, failed
    val syncAttempts: Int = 0,
    val lastSyncAttempt: Date? = null,
    val errorMessage: String? = null
)
