package com.weightloss.betting.data.repository

import com.weightloss.betting.data.remote.NetworkException
import com.weightloss.betting.data.remote.NetworkResult
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import retrofit2.Response
import java.io.IOException
import java.net.SocketTimeoutException

/**
 * Repository 基类 - 提供通用的网络请求处理逻辑
 */
abstract class BaseRepository {
    
    /**
     * 安全执行 API 调用,自动处理异常并返回 NetworkResult
     */
    protected suspend fun <T> safeApiCall(
        apiCall: suspend () -> Response<T>
    ): NetworkResult<T> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiCall()
                
                if (response.isSuccessful) {
                    val body = response.body()
                    if (body != null) {
                        NetworkResult.Success(body)
                    } else {
                        NetworkResult.Error(
                            NetworkException.UnknownError("响应体为空")
                        )
                    }
                } else {
                    // 处理特定的错误状态码
                    // 优先尝试解析响应体中的 detail 或 message 字段，以便前端显示服务器端返回的具体错误信息
                    val errorBody = response.errorBody()?.string() ?: ""
                    val parsedMessage = if (errorBody.isNotEmpty()) {
                        try {
                            val detailRegex = """"detail"\s*:\s*"([^"]+)"""".toRegex()
                            val msgRegex = """"message"\s*:\s*"([^"]+)"""".toRegex()
                            detailRegex.find(errorBody)?.groupValues?.get(1)
                                ?: msgRegex.find(errorBody)?.groupValues?.get(1)
                                ?: errorBody
                        } catch (e: Exception) {
                            errorBody
                        }
                    } else {
                        response.message()
                    }

                    val exception = when (response.code()) {
                        401 -> NetworkException.UnauthorizedError("未授权,请重新登录")
                        402 -> {
                            // 从解析后的消息中提取金额（如果有）
                            val amountRegex = "(\\d+\\.?\\d*)".toRegex()
                            val amount = amountRegex.find(parsedMessage)?.value?.toDoubleOrNull() ?: 0.0
                            NetworkException.PaymentRequiredError(amount, parsedMessage)
                        }
                        422 -> NetworkException.ValidationError(parsedMessage.ifEmpty { "请求参数验证失败" })
                        in 500..599 -> NetworkException.ServerError(response.code(), parsedMessage.ifEmpty { "服务器错误" })
                        else -> NetworkException.ServerError(response.code(), parsedMessage)
                    }
                    NetworkResult.Error(exception)
                }
            } catch (e: NetworkException) {
                // 已经是我们定义的网络异常,直接返回
                NetworkResult.Error(e)
            } catch (e: SocketTimeoutException) {
                NetworkResult.Error(
                    NetworkException.TimeoutError("请求超时,请检查网络连接")
                )
            } catch (e: IOException) {
                NetworkResult.Error(
                    NetworkException.NetworkError("网络连接失败,请检查网络设置")
                )
            } catch (e: Exception) {
                NetworkResult.Error(
                    NetworkException.UnknownError(e.message ?: "未知错误")
                )
            }
        }
    }
}
