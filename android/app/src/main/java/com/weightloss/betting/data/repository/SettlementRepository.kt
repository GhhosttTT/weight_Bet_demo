package com.weightloss.betting.data.repository

import com.weightloss.betting.data.model.SettlementChoiceRequest
import com.weightloss.betting.data.model.SettlementChoiceResponse
import com.weightloss.betting.data.model.SettlementSelectionStatus
import com.weightloss.betting.data.model.DisputeCreateRequest
import com.weightloss.betting.data.model.DisputeResponse
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.NetworkResult
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SettlementRepository @Inject constructor(
    private val apiService: ApiService
) : BaseRepository() {
    suspend fun getStatus(planId: String): NetworkResult<SettlementSelectionStatus> =
        safeApiCall { apiService.getSettlementStatus(planId) }

    suspend fun submit(
        planId: String,
        selfAchieved: Boolean,
        opponentAchieved: Boolean
    ): NetworkResult<SettlementChoiceResponse> = safeApiCall {
        apiService.submitSettlementChoice(
            planId,
            SettlementChoiceRequest(selfAchieved, opponentAchieved)
        )
    }

    suspend fun submitDispute(settlementId: String, reason: String): NetworkResult<DisputeResponse> =
        safeApiCall { apiService.submitDispute(settlementId, DisputeCreateRequest(reason)) }
}
