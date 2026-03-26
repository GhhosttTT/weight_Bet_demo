package com.weightloss.betting.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.google.firebase.messaging.FirebaseMessagingService
import com.google.firebase.messaging.RemoteMessage
import com.weightloss.betting.R
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.NotificationRepository
import com.weightloss.betting.ui.MainActivity
import dagger.hilt.android.AndroidEntryPoint
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import javax.inject.Inject

@AndroidEntryPoint
class FCMService : FirebaseMessagingService() {

    @Inject
    lateinit var notificationRepository: NotificationRepository

    @Inject
    lateinit var tokenManager: TokenManager

    private val serviceScope = CoroutineScope(Dispatchers.IO)

    override fun onNewToken(token: String) {
        super.onNewToken(token)
        
        // 保存新的 FCM token
        serviceScope.launch {
            try {
                notificationRepository.registerDeviceToken(token)
            } catch (e: Exception) {
                // 记录错误,稍后重试
                android.util.Log.e("FCMService", "Failed to register token", e)
            }
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)

        // 处理通知消息
        message.notification?.let { notification ->
            val title = notification.title ?: "减肥对赌"
            val body = notification.body ?: ""
            val type = message.data["type"] ?: "general"
            val relatedId = message.data["relatedId"]

            showNotification(title, body, type, relatedId)
        }

        // 处理数据消息
        if (message.data.isNotEmpty()) {
            handleDataMessage(message.data)
        }
    }

    private fun handleDataMessage(data: Map<String, String>) {
        val type = data["type"] ?: return
        val title = data["title"] ?: "减肥对赌"
        val body = data["body"] ?: ""
        val relatedId = data["relatedId"]

        showNotification(title, body, type, relatedId)
    }

    private fun showNotification(
        title: String,
        body: String,
        type: String,
        relatedId: String?
    ) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // 创建通知渠道 (Android 8.0+)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channelId = getChannelId(type)
            val channelName = getChannelName(type)
            val importance = NotificationManager.IMPORTANCE_HIGH
            val channel = NotificationChannel(channelId, channelName, importance).apply {
                description = "减肥对赌通知"
                enableVibration(true)
                enableLights(true)
            }
            notificationManager.createNotificationChannel(channel)
        }

        // 创建点击意图
        val intent = createNotificationIntent(type, relatedId)
        val pendingIntent = PendingIntent.getActivity(
            this,
            0,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // 构建通知
        val notification = NotificationCompat.Builder(this, getChannelId(type))
            .setSmallIcon(android.R.drawable.ic_dialog_info) // 使用系统图标作为临时方案
            .setContentTitle(title)
            .setContentText(body)
            .setStyle(NotificationCompat.BigTextStyle().bigText(body))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setAutoCancel(true)
            .setContentIntent(pendingIntent)
            .build()

        // 显示通知
        val notificationId = System.currentTimeMillis().toInt()
        notificationManager.notify(notificationId, notification)
    }

    private fun getChannelId(type: String): String {
        return when (type) {
            "invite" -> "channel_invite"
            "plan_active" -> "channel_plan"
            "settlement" -> "channel_settlement"
            "check_in_reminder" -> "channel_reminder"
            else -> "channel_general"
        }
    }

    private fun getChannelName(type: String): String {
        return when (type) {
            "invite" -> "邀请通知"
            "plan_active" -> "计划通知"
            "settlement" -> "结算通知"
            "check_in_reminder" -> "打卡提醒"
            else -> "一般通知"
        }
    }

    private fun createNotificationIntent(type: String, relatedId: String?): Intent {
        val intent = Intent(this, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
            putExtra("notification_type", type)
            relatedId?.let { putExtra("related_id", it) }
        }
        return intent
    }
}
