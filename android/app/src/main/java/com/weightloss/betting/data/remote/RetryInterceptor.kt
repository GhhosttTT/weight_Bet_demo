package com.weightloss.betting.data.remote

import okhttp3.Interceptor
import okhttp3.Response
import java.io.IOException
import java.net.SocketTimeoutException
import javax.inject.Inject

/**
 * 请求重试拦截器 - 自动重试失败的网络请求
 */
class RetryInterceptor @Inject constructor() : Interceptor {
    
    companion object {
        private const val MAX_RETRY_COUNT = 3
        private const val INITIAL_BACKOFF_MS = 1000L
    }
    
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        var response: Response? = null
        var exception: IOException? = null
        var tryCount = 0
        
        while (tryCount < MAX_RETRY_COUNT) {
            try {
                response = chain.proceed(request)
                
                // 如果响应成功或者是客户端错误(4xx),不重试
                if (response.isSuccessful || response.code in 400..499) {
                    return response
                }
                
                // 服务器错误(5xx),关闭响应并准备重试
                response.close()
                
            } catch (e: IOException) {
                exception = e
                
                // 如果不是超时错误,不重试
                if (e !is SocketTimeoutException) {
                    throw e
                }
            }
            
            tryCount++
            
            // 如果还有重试次数,等待后重试
            if (tryCount < MAX_RETRY_COUNT) {
                val backoffTime = INITIAL_BACKOFF_MS * tryCount
                Thread.sleep(backoffTime)
            }
        }
        
        // 如果所有重试都失败,抛出异常或返回最后的响应
        exception?.let { throw it }
        return response ?: throw IOException("请求失败且无响应")
    }
}
