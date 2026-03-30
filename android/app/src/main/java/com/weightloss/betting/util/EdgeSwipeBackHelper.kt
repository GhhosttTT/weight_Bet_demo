package com.weightloss.betting.util

import android.app.Activity
import android.graphics.Rect
import android.view.MotionEvent
import android.view.View
import androidx.fragment.app.FragmentActivity
import androidx.fragment.app.FragmentManager
import com.weightloss.betting.R

/**
 * 边缘滑动返回工具类 - 实现类似 iOS 的边缘右滑返回上一页功能
 */
object EdgeSwipeBackHelper {

    private const val SWIPE_EDGE_WIDTH_DP = 20 // 边缘区域宽度（dp）
    private const val MIN_SWIPE_DISTANCE_DP = 100 // 最小滑动距离（dp）
    private const val MAX_VELOCITY_DP = 1000 // 最大速度阈值

    /**
     * 为 Activity 启用边缘滑动返回
     */
    fun enableForActivity(activity: Activity) {
        val rootView = activity.findViewById<View>(android.R.id.content)
        setupSwipeBack(rootView, activity)
    }

    /**
     * 为 FragmentActivity 启用边缘滑动返回（支持 Fragment）
     */
    fun enableForFragmentActivity(activity: FragmentActivity) {
        val rootView = activity.findViewById<View>(android.R.id.content)
        setupSwipeBack(rootView, activity)
    }

    private fun setupSwipeBack(rootView: View, activity: Activity) {
        var initialX = 0f
        var isSwiping = false

        rootView.setOnTouchListener { _, event ->
            when (event.action) {
                MotionEvent.ACTION_DOWN -> {
                    // 检查是否在屏幕左边缘
                    if (event.x <= dpToPx(activity, SWIPE_EDGE_WIDTH_DP)) {
                        initialX = event.x
                        isSwiping = true
                        true
                    } else {
                        false
                    }
                }
                MotionEvent.ACTION_MOVE -> {
                    if (isSwiping) {
                        val deltaX = event.x - initialX
                        // 向右滑动超过阈值
                        if (deltaX > dpToPx(activity, MIN_SWIPE_DISTANCE_DP)) {
                            performBackNavigation(activity)
                            isSwiping = false
                            true
                        } else {
                            true
                        }
                    } else {
                        false
                    }
                }
                MotionEvent.ACTION_UP, MotionEvent.ACTION_CANCEL -> {
                    isSwiping = false
                    false
                }
                else -> false
            }
        }
    }

    /**
     * 执行返回操作
     */
    @Suppress("DEPRECATION")
    private fun performBackNavigation(activity: Activity) {
        when (activity) {
            is FragmentActivity -> {
                val fragmentManager = activity.supportFragmentManager
                if (fragmentManager.backStackEntryCount > 0) {
                    // 如果是 FragmentActivity 且有 Fragment 返回栈
                    fragmentManager.popBackStack()
                } else {
                    // 否则关闭当前 Activity
                    activity.onBackPressed()
                }
            }
            else -> {
                // 普通 Activity 直接返回
                activity.onBackPressed()
            }
        }
    }

    /**
     * DP 转 PX
     */
    private fun dpToPx(activity: Activity, dp: Int): Float {
        return dp * activity.resources.displayMetrics.density
    }
}
