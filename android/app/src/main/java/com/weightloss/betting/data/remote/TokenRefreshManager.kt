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
     * 读取 JWT payload 中的 exp（Unix 秒）。
     * JWT 的签名校验仍由服务端完成；客户端只用 exp 决定是否提前刷新。
     * 格式异常或缺失 exp 时按即将过期处理，避免继续携带不可信令牌请求接口。
     */
    private fun isTokenExpiringSoon(token: String): Boolean {
        return JwtTokenUtils.isExpiringSoon(token)
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
