package com.weightloss.betting.util

import android.content.Context
import androidx.appcompat.app.AlertDialog
import com.google.android.material.dialog.MaterialAlertDialogBuilder
import com.weightloss.betting.R

/**
 * 对话框工具类
 */
object DialogUtils {
    
    /**
     * 显示加载对话框
     */
    fun showLoadingDialog(context: Context, message: String = "加载中..."): AlertDialog {
        return MaterialAlertDialogBuilder(context)
            .setMessage(message)
            .setCancelable(false)
            .create()
            .apply { show() }
    }
    
    /**
     * 显示错误对话框
     */
    fun showErrorDialog(
        context: Context,
        title: String = "错误",
        message: String,
        onDismiss: (() -> Unit)? = null
    ) {
        MaterialAlertDialogBuilder(context)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton("确定") { dialog, _ ->
                dialog.dismiss()
                onDismiss?.invoke()
            }
            .show()
    }
    
    /**
     * 显示确认对话框
     */
    fun showConfirmDialog(
        context: Context,
        title: String,
        message: String,
        positiveText: String = "确定",
        negativeText: String = "取消",
        onConfirm: () -> Unit,
        onCancel: (() -> Unit)? = null
    ) {
        MaterialAlertDialogBuilder(context)
            .setTitle(title)
            .setMessage(message)
            .setPositiveButton(positiveText) { dialog, _ ->
                dialog.dismiss()
                onConfirm()
            }
            .setNegativeButton(negativeText) { dialog, _ ->
                dialog.dismiss()
                onCancel?.invoke()
            }
            .show()
    }
    
    /**
     * 显示网络超时对话框
     */
    fun showNetworkTimeoutDialog(
        context: Context,
        onRetry: () -> Unit
    ) {
        MaterialAlertDialogBuilder(context)
            .setTitle("网络超时")
            .setMessage("请求超时,请检查网络连接后重试")
            .setPositiveButton("重试") { dialog, _ ->
                dialog.dismiss()
                onRetry()
            }
            .setNegativeButton("取消") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
    
    /**
     * 显示网络错误对话框
     */
    fun showNetworkErrorDialog(
        context: Context,
        onRetry: () -> Unit
    ) {
        MaterialAlertDialogBuilder(context)
            .setTitle("网络错误")
            .setMessage("网络连接失败,请检查网络设置后重试")
            .setPositiveButton("重试") { dialog, _ ->
                dialog.dismiss()
                onRetry()
            }
            .setNegativeButton("取消") { dialog, _ ->
                dialog.dismiss()
            }
            .show()
    }
}
