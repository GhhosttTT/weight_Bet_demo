package com.weightloss.betting.di

import android.content.Context
import androidx.room.Room
import com.weightloss.betting.data.local.AppDatabase
import com.weightloss.betting.data.local.dao.BettingPlanDao
import com.weightloss.betting.data.local.dao.CheckInDao
import com.weightloss.betting.data.local.dao.OfflineCheckInDao
import com.weightloss.betting.data.local.dao.UserDao
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * 数据库模块 - 提供 Room 数据库依赖
 */
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            AppDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration()
            .build()
    }
    
    @Provides
    @Singleton
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
    
    @Provides
    @Singleton
    fun provideBettingPlanDao(database: AppDatabase): BettingPlanDao {
        return database.bettingPlanDao()
    }
    
    @Provides
    @Singleton
    fun provideCheckInDao(database: AppDatabase): CheckInDao {
        return database.checkInDao()
    }
    
    @Provides
    @Singleton
    fun provideOfflineCheckInDao(database: AppDatabase): OfflineCheckInDao {
        return database.offlineCheckInDao()
    }
}
