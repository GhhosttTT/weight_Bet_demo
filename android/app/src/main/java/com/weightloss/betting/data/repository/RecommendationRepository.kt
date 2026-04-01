package com.weightloss.betting.data.repository

import android.util.Log
import com.weightloss.betting.data.local.RecommendationCacheManager
import com.weightloss.betting.data.model.RecommendationResponse
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import kotlinx.coroutines.GlobalScope
import kotlinx.coroutines.launch
import kotlinx.coroutines.withTimeout
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RecommendationRepository @Inject constructor(
    private val apiService: ApiService,
    private val cacheManager: RecommendationCacheManager
) : BaseRepository() {

    suspend fun getRecommendation(useCache: Boolean = true): NetworkResult<RecommendationResponse> {
        if (useCache) {
            cacheManager.getCachedRecommendation()?.let {
                return NetworkResult.Success(it)
            }
        }
        return safeApiCall { apiService.getRecommendation(useCache) }
    }

    suspend fun refreshRecommendation(): NetworkResult<RecommendationResponse> {
        return safeApiCall { apiService.refreshRecommendation() }
    }

    fun cacheRecommendation(recommendation: RecommendationResponse) {
        cacheManager.cacheRecommendation(recommendation)
    }

    fun getCachedRecommendation(): RecommendationResponse? {
        return cacheManager.getCachedRecommendation()
    }

    fun fetchAndCacheRecommendationAsync() {
        Log.d("RecommendationRepository", "fetchAndCacheRecommendationAsync() started")
        GlobalScope.launch {
            try {
                Log.d("RecommendationRepository", "Calling getRecommendation(useCache = false)")
                withTimeout(30000) {
                    when (val result = getRecommendation(useCache = false)) {
                        is NetworkResult.Success -> {
                            Log.d("RecommendationRepository", "Recommendation fetched successfully!")
                            Log.d("RecommendationRepository", "Caching recommendation...")
                            cacheRecommendation(result.data)
                            Log.d("RecommendationRepository", "Recommendation cached successfully!")
                        }
                        is NetworkResult.Error -> {
                            Log.e("RecommendationRepository", "Failed to fetch recommendation: ${result.exception.message}")
                        }
                        else -> {
                            Log.d("RecommendationRepository", "Recommendation result is something else")
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("RecommendationRepository", "Exception while fetching recommendation", e)
            }
        }
    }

    fun refreshAndCacheRecommendationAsync() {
        Log.d("RecommendationRepository", "refreshAndCacheRecommendationAsync() started")
        GlobalScope.launch {
            try {
                Log.d("RecommendationRepository", "Calling refreshRecommendation()")
                withTimeout(30000) {
                    when (val result = refreshRecommendation()) {
                        is NetworkResult.Success -> {
                            Log.d("RecommendationRepository", "Recommendation refreshed successfully!")
                            Log.d("RecommendationRepository", "Caching recommendation...")
                            cacheRecommendation(result.data)
                            Log.d("RecommendationRepository", "Recommendation cached successfully!")
                        }
                        is NetworkResult.Error -> {
                            Log.e("RecommendationRepository", "Failed to refresh recommendation: ${result.exception.message}")
                        }
                        else -> {
                            Log.d("RecommendationRepository", "Recommendation result is something else")
                        }
                    }
                }
            } catch (e: Exception) {
                Log.e("RecommendationRepository", "Exception while refreshing recommendation", e)
            }
        }
    }
}
