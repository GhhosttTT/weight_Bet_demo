package com.weightloss.betting.data.remote

import android.content.Context
import android.util.Log
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
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
    
    companion object {
        private const val TAG = "TokenManager"
        private val ACCESS_TOKEN_KEY = stringPreferencesKey("access_token")
        private val REFRESH_TOKEN_KEY = stringPreferencesKey("refresh_token")
        private val USER_ID_KEY = stringPreferencesKey("user_id")
    }
    
    suspend fun saveTokens(accessToken: String, refreshToken: String, userId: String? = null) {
        val accessPreview = if (accessToken.length > 20) accessToken.take(20) + "..." else accessToken
        val refreshPreview = if (refreshToken.length > 20) refreshToken.take(20) + "..." else refreshToken
        Log.d(TAG, "Saving tokens - Access: $accessPreview, Refresh: $refreshPreview, UserId: $userId")
        context.dataStore.edit { preferences ->
            preferences[ACCESS_TOKEN_KEY] = accessToken
            preferences[REFRESH_TOKEN_KEY] = refreshToken
            if (userId != null) {
                preferences[USER_ID_KEY] = userId
            }
        }
        Log.d(TAG, "Tokens saved successfully")
    }
    
    suspend fun getAccessToken(): String? {
        val token = context.dataStore.data.map { preferences ->
            preferences[ACCESS_TOKEN_KEY]
        }.first()
        Log.d(TAG, "Retrieved access token: ${if (token.isNullOrEmpty()) "EMPTY" else "EXISTS (${token.take(20)}...)"}")
        return token
    }
    
    suspend fun getRefreshToken(): String? {
        val token = context.dataStore.data.map { preferences ->
            preferences[REFRESH_TOKEN_KEY]
        }.first()
        Log.d(TAG, "Retrieved refresh token: ${if (token.isNullOrEmpty()) "EMPTY" else "EXISTS"}")
        return token
    }
    
    suspend fun getUserId(): String? {
        val userId = context.dataStore.data.map { preferences ->
            preferences[USER_ID_KEY]
        }.first()
        Log.d(TAG, "Retrieved user ID: ${userId ?: "EMPTY"}")
        return userId
    }
    
    suspend fun clearTokens() {
        Log.d(TAG, "Clearing tokens")
        context.dataStore.edit { preferences ->
            preferences.remove(ACCESS_TOKEN_KEY)
            preferences.remove(REFRESH_TOKEN_KEY)
            preferences.remove(USER_ID_KEY)
        }
        Log.d(TAG, "Tokens cleared")
    }
}
