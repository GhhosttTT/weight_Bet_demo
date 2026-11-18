package com.weightloss.betting

import android.app.Application
import com.stripe.android.PaymentConfiguration
import com.xuexiang.xui.XUI
import dagger.hilt.android.HiltAndroidApp

/**
 * Application 类 - Hilt 依赖注入入口
 */
@HiltAndroidApp
class WeightLossBettingApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // 初始化 XUI
        XUI.init(this)
        XUI.debug(true)
        val publishableKey = getString(com.weightloss.betting.R.string.stripe_publishable_key)
        if (publishableKey.isNotBlank() && !publishableKey.contains("replace_me")) {
            PaymentConfiguration.init(this, publishableKey)
        }
    }
}
