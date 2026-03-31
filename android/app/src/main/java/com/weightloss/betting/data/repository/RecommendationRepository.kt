package com.weightloss.betting.data.repository

import com.weightloss.betting.data.model.RecommendationResponse
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RecommendationRepository @Inject constructor(
    private val apiService: ApiService
) : BaseRepository() {
    
    suspend fun getRecommendation(useCache: Boolean = true): NetworkResult<RecommendationResponse> {
        return safeApiCall { apiService.getRecommendation(useCache) }
    }
    
    suspend fun refreshRecommendation(): NetworkResult<RecommendationResponse> {
        return safeApiCall { apiService.refreshRecommendation() }
    }
}
