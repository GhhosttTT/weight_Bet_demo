package com.weightloss.betting.data.remote

import android.util.Log
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Request
import okhttp3.Response
import javax.inject.Inject
import javax.inject.Provider

/**
 * 认证拦截器 - 自动添加 JWT 令牌到请求头，并在 401 时自动刷新令牌
 */
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager,
    private val authRepositoryProvider: Provider<com.weightloss.betting.data.repository.AuthRepository>
) : Interceptor {
    
    companion object {
        private const val TAG = "AuthInterceptor"
    }
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val path = originalRequest.url.encodedPath
        
        Log.d(TAG, "Intercepting request: $path")
        
        // 如果是登录/注册/刷新令牌请求，直接放行
        if (isAuthRequest(path)) {
            Log.d(TAG, "Proceeding without token (auth request)")
            return chain.proceed(originalRequest)
        }
        
        // 获取访问令牌
        val token = runBlocking {
            tokenManager.getAccessToken()
        }
        
        Log.d(TAG, "Token retrieved: ${if (token.isNullOrEmpty()) "EMPTY" else "EXISTS"}")
        
        // 如果没有令牌，直接放行（让后续逻辑处理）
        if (token.isNullOrEmpty()) {
            Log.d(TAG, "Proceeding without token (no token available)")
            return chain.proceed(originalRequest)
        }
        
        // 添加 Authorization 头并执行请求
        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()
        
        Log.d(TAG, "Added Authorization header")
        
        var response = chain.proceed(authenticatedRequest)
        
        // 如果收到 401 响应，尝试刷新令牌
        if (response.code == 401) {
            Log.d(TAG, "Received 401, attempting to refresh token")
            
            response.close()
            
            val refreshSuccess = runBlocking {
                refreshToken()
            }
            
            if (refreshSuccess) {
                Log.d(TAG, "Token refreshed successfully, retrying request")
                
                // 获取新的令牌并重试请求
                val newToken = runBlocking {
                    tokenManager.getAccessToken()
                }
                
                if (newToken != null) {
                    val newRequest = originalRequest.newBuilder()
                        .header("Authorization", "Bearer $newToken")
                        .build()
                    
                    return chain.proceed(newRequest)
                }
            } else {
                Log.d(TAG, "Token refresh failed")
            }
        }
        
        return response
    }
    
    private suspend fun refreshToken(): Boolean {
        val refreshToken = tokenManager.getRefreshToken() ?: return false
        
        // 使用 Provider 延迟获取 AuthRepository，避免循环依赖
        val authRepository = authRepositoryProvider.get()
        
        return when (val result = authRepository.refreshToken()) {
            is NetworkResult.Success -> {
                Log.d(TAG, "Token refresh successful")
                true
            }
            is NetworkResult.Error -> {
                Log.e(TAG, "Token refresh failed: ${result.exception.message}")
                tokenManager.clearTokens()
                false
            }
            is NetworkResult.Loading -> false
        }
    }
    
    private fun isAuthRequest(path: String): Boolean {
        return path.contains("/auth/login") ||
                path.contains("/auth/register") ||
                path.contains("/auth/google") ||
                path.contains("/auth/refresh")
    }
}
