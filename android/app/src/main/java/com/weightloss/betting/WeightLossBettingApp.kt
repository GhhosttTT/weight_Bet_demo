package com.weightloss.betting

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

/**
 * Application 类 - Hilt 依赖注入入口
 */
@HiltAndroidApp
class WeightLossBettingApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        // 初始化应用级别的配置
    }
}
