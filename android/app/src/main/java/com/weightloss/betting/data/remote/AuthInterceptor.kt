package com.weightloss.betting.data.remote

import android.util.Log
import kotlinx.coroutines.runBlocking
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

/**
 * 认证拦截器 - 自动添加 JWT 令牌到请求头
 */
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    
    companion object {
        private const val TAG = "AuthInterceptor"
    }
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val originalRequest = chain.request()
        val path = originalRequest.url.encodedPath
        
        Log.d(TAG, "Intercepting request: $path")
        
        // 获取访问令牌
        val token = runBlocking {
            tokenManager.getAccessToken()
        }
        
        Log.d(TAG, "Token retrieved: ${if (token.isNullOrEmpty()) "EMPTY" else "EXISTS (${token.take(20)}...)"}")
        
        // 如果没有令牌或者是登录/注册请求,直接放行
        if (token.isNullOrEmpty() || isAuthRequest(path)) {
            Log.d(TAG, "Proceeding without token (isAuthRequest: ${isAuthRequest(path)})")
            return chain.proceed(originalRequest)
        }
        
        // 添加 Authorization 头
        val authenticatedRequest = originalRequest.newBuilder()
            .header("Authorization", "Bearer $token")
            .build()
        
        Log.d(TAG, "Added Authorization header")
        
        return chain.proceed(authenticatedRequest)
    }
    
    private fun isAuthRequest(path: String): Boolean {
        return path.contains("/auth/login") ||
                path.contains("/auth/register") ||
                path.contains("/auth/google")
    }
}
