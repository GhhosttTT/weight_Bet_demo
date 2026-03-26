package com.weightloss.betting.di

import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.*
import com.weightloss.betting.data.local.CacheManager
import com.weightloss.betting.data.local.OfflineSyncService
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

/**
 * Repository 模块 - 提供 Repository 依赖
 */
@Module
@InstallIn(SingletonComponent::class)
object RepositoryModule {
    
    @Provides
    @Singleton
    fun provideAuthRepository(
        apiService: ApiService,
        tokenManager: TokenManager
    ): AuthRepository {
        return AuthRepository(apiService, tokenManager)
    }
    
    @Provides
    @Singleton
    fun provideUserRepository(
        apiService: ApiService,
        cacheManager: CacheManager
    ): UserRepository {
        return UserRepository(apiService, cacheManager)
    }
    
    @Provides
    @Singleton
    fun provideBettingPlanRepository(
        apiService: ApiService,
        cacheManager: CacheManager
    ): BettingPlanRepository {
        return BettingPlanRepository(apiService, cacheManager)
    }
    
    @Provides
    @Singleton
    fun provideCheckInRepository(
        apiService: ApiService,
        cacheManager: CacheManager
    ): CheckInRepository {
        return CheckInRepository(apiService, cacheManager)
    }
    
    @Provides
    @Singleton
    fun providePaymentRepository(
        apiService: ApiService
    ): PaymentRepository {
        return PaymentRepository(apiService)
    }
    
    @Provides
    @Singleton
    fun provideSocialRepository(
        apiService: ApiService
    ): SocialRepository {
        return SocialRepository(apiService)
    }
}
