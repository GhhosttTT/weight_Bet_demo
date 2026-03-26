package com.weightloss.betting.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.TypeConverters
import com.weightloss.betting.data.local.dao.BettingPlanDao
import com.weightloss.betting.data.local.dao.CheckInDao
import com.weightloss.betting.data.local.dao.OfflineCheckInDao
import com.weightloss.betting.data.local.dao.UserDao
import com.weightloss.betting.data.local.entity.BettingPlanEntity
import com.weightloss.betting.data.local.entity.CheckInEntity
import com.weightloss.betting.data.local.entity.OfflineCheckInEntity
import com.weightloss.betting.data.local.entity.UserEntity

/**
 * Room 数据库配置
 */
@Database(
    entities = [
        UserEntity::class,
        BettingPlanEntity::class,
        CheckInEntity::class,
        OfflineCheckInEntity::class
    ],
    version = 2,
    exportSchema = false
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    
    abstract fun userDao(): UserDao
    abstract fun bettingPlanDao(): BettingPlanDao
    abstract fun checkInDao(): CheckInDao
    abstract fun offlineCheckInDao(): OfflineCheckInDao
    
    companion object {
        const val DATABASE_NAME = "weight_loss_betting_db"
    }
}
