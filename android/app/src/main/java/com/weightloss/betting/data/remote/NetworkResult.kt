package com.weightloss.betting.data.remote

/**
 * 网络请求结果封装
 */
sealed class NetworkResult<out T> {
    data class Success<T>(val data: T) : NetworkResult<T>()
    data class Error(val exception: NetworkException) : NetworkResult<Nothing>()
    object Loading : NetworkResult<Nothing>()
}

/**
 * 网络异常类型
 */
sealed class NetworkException(message: String) : Exception(message) {
    class NetworkError(message: String = "网络连接失败") : NetworkException(message)
    class ServerError(val code: Int, message: String = "服务器错误") : NetworkException(message)
    class UnauthorizedError(message: String = "未授权,请重新登录") : NetworkException(message)
    class ValidationError(message: String = "数据验证失败") : NetworkException(message)
    class TimeoutError(message: String = "请求超时") : NetworkException(message)
    class PaymentRequiredError(val requiredAmount: Double, message: String = "余额不足，需要充值") : NetworkException(message)
    class UnknownError(message: String = "未知错误") : NetworkException(message)
}
