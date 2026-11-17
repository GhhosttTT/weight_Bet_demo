package com.weightloss.betting.data.remote

import android.util.Base64
import org.json.JSONObject
import java.nio.charset.StandardCharsets

/** 客户端只读取 JWT 的 exp 以决定是否刷新；令牌签名仍由服务端校验。 */
object JwtTokenUtils {
    private const val EXPIRY_LEEWAY_SECONDS = 60L

    fun isExpiringSoon(token: String, nowSeconds: Long = System.currentTimeMillis() / 1000L): Boolean {
        return try {
            val segments = token.split('.')
            if (segments.size != 3) return true

            val payload = Base64.decode(
                segments[1],
                Base64.URL_SAFE or Base64.NO_WRAP or Base64.NO_PADDING
            ).toString(StandardCharsets.UTF_8)
            val expiresAt = JSONObject(payload).optLong("exp", 0L)
            expiresAt <= 0L || expiresAt - nowSeconds <= EXPIRY_LEEWAY_SECONDS
        } catch (_: Exception) {
            true
        }
    }
}
