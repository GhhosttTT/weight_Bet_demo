package com.weightloss.betting.data.remote

/**
 * API 错误响应模型
 */
data class ErrorResponse(
    val error: String? = null,
    val message: String? = null,
    val detail: String? = null,
    val statusCode: Int? = null
)
