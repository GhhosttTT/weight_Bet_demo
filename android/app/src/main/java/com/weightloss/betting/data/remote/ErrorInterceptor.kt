package com.weightloss.betting.data.remote

import android.util.Log
import com.google.gson.Gson
import okhttp3.Interceptor
import okhttp3.Response
import javax.inject.Inject

/**
 * 错误处理拦截器 - 记录错误但不抛出异常
 * 让 Repository 层的 safeApiCall 处理错误响应
 */
class ErrorInterceptor @Inject constructor(
    private val gson: Gson
) : Interceptor {
    
    companion object {
        private const val TAG = "ErrorInterceptor"
    }
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        val response = chain.proceed(request)
        
        // 如果响应成功,直接返回
        if (response.isSuccessful) {
            return response
        }
        
        // 记录错误但不抛出异常
        val errorBody = response.peekBody(Long.MAX_VALUE).string()
        val errorResponse = try {
            gson.fromJson(errorBody, ErrorResponse::class.java)
        } catch (e: Exception) {
            null
        }
        
        val errorMessage = errorResponse?.message ?: response.message
        Log.w(TAG, "HTTP ${response.code}: $errorMessage for ${request.url}")
        
        // 返回响应，让 Repository 层处理
        return response
    }
}
