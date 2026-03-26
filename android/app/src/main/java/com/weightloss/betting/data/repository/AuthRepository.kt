package com.weightloss.betting.data.repository

import com.weightloss.betting.data.model.*
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 认证 Repository - 处理用户认证相关的数据操作
 */
@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val tokenManager: TokenManager
) : BaseRepository() {
    
    /**
     * 用户注册
     */
    suspend fun register(request: RegisterRequest): NetworkResult<AuthResult> {
        val result = safeApiCall { apiService.register(request) }
        
        // 如果注册成功,保存令牌和用户ID
        if (result is NetworkResult.Success) {
            tokenManager.saveTokens(
                result.data.accessToken,
                result.data.refreshToken,
                result.data.userId
            )
        }
        
        return result
    }
    
    /**
     * 用户登录
     */
    suspend fun login(request: LoginRequest): NetworkResult<AuthResult> {
        val result = safeApiCall { apiService.login(request) }
                
        // 如果登录成功，保存令牌和用户 ID
        if (result is NetworkResult.Success) {
            tokenManager.saveTokens(
                result.data.accessToken,
                result.data.refreshToken,
                result.data.userId
            )
        }
                
        return result
    }
        
    /**
     * 获取待处理操作（邀请/Double Check）
     */
    suspend fun getPendingActions(): NetworkResult<PendingActionsResponse> {
        return safeApiCall { apiService.getPendingActions() }
    }
    
    /**
     * Google 登录
     */
    suspend fun googleLogin(idToken: String): NetworkResult<AuthResult> {
        val request = GoogleLoginRequest(idToken)
        val result = safeApiCall { apiService.googleLogin(request) }
        
        // 如果登录成功,保存令牌和用户ID
        if (result is NetworkResult.Success) {
            tokenManager.saveTokens(
                result.data.accessToken,
                result.data.refreshToken,
                result.data.userId
            )
        }
        
        return result
    }
    
    /**
     * 刷新令牌
     */
    suspend fun refreshToken(): NetworkResult<AuthResult> {
        val refreshToken = tokenManager.getRefreshToken()
            ?: return NetworkResult.Error(
                com.weightloss.betting.data.remote.NetworkException.UnauthorizedError("刷新令牌不存在")
            )
        
        val request = RefreshTokenRequest(refreshToken)
        val result = safeApiCall { apiService.refreshToken(request) }
        
        // 如果刷新成功,保存新令牌和用户ID
        if (result is NetworkResult.Success) {
            tokenManager.saveTokens(
                result.data.accessToken,
                result.data.refreshToken,
                result.data.userId
            )
        }
        
        return result
    }
    
    /**
     * 登出
     */
    suspend fun logout() {
        tokenManager.clearTokens()
    }
}
