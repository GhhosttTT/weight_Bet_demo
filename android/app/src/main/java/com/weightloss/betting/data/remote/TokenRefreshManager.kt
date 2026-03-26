package com.weightloss.betting.data.remote

import com.weightloss.betting.data.repository.AuthRepository
import kotlinx.coroutines.runBlocking
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 令牌刷新管理器 - 处理令牌过期和自动刷新
 */
@Singleton
class TokenRefreshManager @Inject constructor(
    private val tokenManager: TokenManager,
    private val authRepository: AuthRepository
) {
    
    /**
     * 检查令牌是否过期并自动刷新
     * 
     * @return true 如果令牌有效或刷新成功, false 如果刷新失败
     */
    suspend fun ensureValidToken(): Boolean {
        val accessToken = tokenManager.getAccessToken()
        
        // 如果没有访问令牌,返回 false
        if (accessToken == null) {
            return false
        }
        
        // 检查令牌是否即将过期 (这里简化处理,实际应该解析 JWT 检查过期时间)
        // 如果令牌即将过期,尝试刷新
        if (isTokenExpiringSoon(accessToken)) {
            return refreshToken()
        }
        
        return true
    }
    
    /**
     * 刷新令牌
     */
    private suspend fun refreshToken(): Boolean {
        return when (val result = authRepository.refreshToken()) {
            is NetworkResult.Success -> true
            is NetworkResult.Error -> {
                // 刷新失败,清除令牌
                tokenManager.clearTokens()
                false
            }
            is NetworkResult.Loading -> false
        }
    }
    
    /**
     * 检查令牌是否即将过期
     * 
     * 注意: 这是简化实现,实际应该解析 JWT 的 exp 字段
     */
    private fun isTokenExpiringSoon(token: String): Boolean {
        // TODO: 实现 JWT 解析和过期时间检查
        // 这里简化处理,假设令牌总是有效
        return false
    }
    
    /**
     * 同步检查令牌有效性 (用于拦截器)
     */
    fun ensureValidTokenSync(): Boolean {
        return runBlocking {
            ensureValidToken()
        }
    }
}
