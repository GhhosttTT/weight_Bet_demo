package com.weightloss.betting.data.local.entity

import androidx.room.Entity
import androidx.room.PrimaryKey
import java.util.Date

/**
 * 用户本地实体
 */
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey
    val id: String,
    val email: String,
    val nickname: String,
    val gender: String,
    val age: Int,
    val height: Double,
    val currentWeight: Double,
    val targetWeight: Double?,
    val createdAt: Date,
    val updatedAt: Date
)
