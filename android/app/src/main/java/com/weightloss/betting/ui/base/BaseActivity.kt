package com.weightloss.betting.ui.base

import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity
import com.weightloss.betting.util.EdgeSwipeBackHelper

/**
 * 基础 Activity - 统一支持边缘滑动返回
 */
abstract class BaseActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // 启用边缘滑动返回
        EdgeSwipeBackHelper.enableForActivity(this)
    }
}
