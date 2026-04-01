package com.weightloss.betting.data.local

import android.content.Context
import com.google.gson.Gson
import com.weightloss.betting.data.model.RecommendationResponse
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RecommendationCacheManager @Inject constructor(
    @ApplicationContext private val context: Context
) {
    private val prefs = context.getSharedPreferences("recommendation_cache", Context.MODE_PRIVATE)
    private val gson = Gson()
    private val KEY_RECOMMENDATION = "cached_recommendation"

    fun cacheRecommendation(recommendation: RecommendationResponse) {
        val json = gson.toJson(recommendation)
        prefs.edit().putString(KEY_RECOMMENDATION, json).apply()
    }

    fun getCachedRecommendation(): RecommendationResponse? {
        val json = prefs.getString(KEY_RECOMMENDATION, null) ?: return null
        return try {
            gson.fromJson(json, RecommendationResponse::class.java)
        } catch (e: Exception) {
            null
        }
    }

    fun clearCache() {
        prefs.edit().remove(KEY_RECOMMENDATION).apply()
    }
}
