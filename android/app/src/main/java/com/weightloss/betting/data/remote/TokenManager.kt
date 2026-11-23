package com.weightloss.betting.data.remote

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.sync.Mutex
import kotlinx.coroutines.sync.withLock
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import javax.inject.Inject
import javax.inject.Singleton

/**
 * 令牌管理器 - 管理 JWT 访问令牌和刷新令牌
 */
@Singleton
class TokenManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "auth_prefs")
    private val migrationMutex = Mutex()
    private var migrationChecked = false
    private val encryptedPreferences: SharedPreferences by lazy {
        val masterKey = MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build()
        EncryptedSharedPreferences.create(
            context,
            "encrypted_auth_prefs",
            masterKey,
            EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
            EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
        )
    }
    
    companion object {
        private const val TAG = "TokenManager"
        private val ACCESS_TOKEN_KEY = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN_KEY = stringPreferencesKey("refresh_token")
        private val USER_ID_KEY = stringPreferencesKey("user_id")
        private val PENDING_CHARGE_KEY = stringPreferencesKey("pending_charge_transaction_id")
    }
    
    suspend fun saveTokens(accessToken: String, refreshToken: String, userId: String? = null) {
        migrateLegacyStorageIfNeeded()
        Log.d(TAG, "Saving authentication tokens (userId present: ${!userId.isNullOrBlank()})")
        encryptedPreferences.edit().apply {
            putString(ACCESS_TOKEN_KEY.name, accessToken)
            putString(REFRESH_TOKEN_KEY.name, refreshToken)
            if (userId != null) putString(USER_ID_KEY.name, userId)
            apply()
        }
        Log.d(TAG, "Tokens saved successfully")
    }
    
    suspend fun getAccessToken(): String? {
        migrateLegacyStorageIfNeeded()
        val token = encryptedPreferences.getString(ACCESS_TOKEN_KEY.name, null)
        Log.d(TAG, "Retrieved access token: ${if (token.isNullOrEmpty()) "EMPTY" else "EXISTS"}")
        return token
    }
    
    suspend fun getRefreshToken(): String? {
        migrateLegacyStorageIfNeeded()
        val token = encryptedPreferences.getString(REFRESH_TOKEN_KEY.name, null)
        Log.d(TAG, "Retrieved refresh token: ${if (token.isNullOrEmpty()) "EMPTY" else "EXISTS"}")
        return token
    }
    
    suspend fun getUserId(): String? {
        migrateLegacyStorageIfNeeded()
        val userId = encryptedPreferences.getString(USER_ID_KEY.name, null)
        Log.d(TAG, "Retrieved user ID: ${if (userId.isNullOrEmpty()) "EMPTY" else "EXISTS"}")
        return userId
    }
    
    suspend fun clearTokens() {
        migrateLegacyStorageIfNeeded()
        Log.d(TAG, "Clearing tokens")
        encryptedPreferences.edit().apply {
            remove(ACCESS_TOKEN_KEY.name)
            remove(REFRESH_TOKEN_KEY.name)
            remove(USER_ID_KEY.name)
            apply()
        }
        Log.d(TAG, "Tokens cleared")
    }

    suspend fun savePendingCharge(transactionId: String) {
        migrateLegacyStorageIfNeeded()
        encryptedPreferences.edit().putString(PENDING_CHARGE_KEY.name, transactionId).apply()
    }

    suspend fun getPendingCharge(): String? {
        migrateLegacyStorageIfNeeded()
        return encryptedPreferences.getString(PENDING_CHARGE_KEY.name, null)
    }

    suspend fun clearPendingCharge() {
        migrateLegacyStorageIfNeeded()
        encryptedPreferences.edit().remove(PENDING_CHARGE_KEY.name).apply()
    }

    /** 一次性迁移旧 DataStore，避免升级后让已有用户被迫重新登录。 */
    private suspend fun migrateLegacyStorageIfNeeded() {
        if (migrationChecked) return
        migrationMutex.withLock {
            if (migrationChecked) return
            val legacy = context.dataStore.data.first()
            val encryptedEditor = encryptedPreferences.edit()
            if (!encryptedPreferences.contains(ACCESS_TOKEN_KEY.name)) {
                legacy[ACCESS_TOKEN_KEY]?.let { encryptedEditor.putString(ACCESS_TOKEN_KEY.name, it) }
            }
            if (!encryptedPreferences.contains(REFRESH_TOKEN_KEY.name)) {
                legacy[REFRESH_TOKEN_KEY]?.let { encryptedEditor.putString(REFRESH_TOKEN_KEY.name, it) }
            }
            if (!encryptedPreferences.contains(USER_ID_KEY.name)) {
                legacy[USER_ID_KEY]?.let { encryptedEditor.putString(USER_ID_KEY.name, it) }
            }
            if (!encryptedPreferences.contains(PENDING_CHARGE_KEY.name)) {
                legacy[PENDING_CHARGE_KEY]?.let { encryptedEditor.putString(PENDING_CHARGE_KEY.name, it) }
            }
            // Complete the encrypted write before deleting the legacy file.
            encryptedEditor.commit()
            if (legacy.asMap().isNotEmpty()) context.dataStore.edit { it.clear() }
            migrationChecked = true
        }
    }
}
