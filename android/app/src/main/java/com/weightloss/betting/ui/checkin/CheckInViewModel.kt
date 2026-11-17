package com.weightloss.betting.ui.checkin

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.CheckIn
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.remote.TokenManager
import com.weightloss.betting.data.repository.BettingPlanRepository
import com.weightloss.betting.data.repository.CheckInData
import com.weightloss.betting.data.repository.CheckInRepository
import com.weightloss.betting.data.repository.RecommendationRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import javax.inject.Inject

sealed class CheckInState {
    object Idle : CheckInState()
    object Loading : CheckInState()
    data class Success(val checkIn: CheckIn) : CheckInState()
    data class Error(val message: String) : CheckInState()
}

sealed class PhotoUploadState {
    object Idle : PhotoUploadState()
    object Loading : PhotoUploadState()
    data class Success(val photoUrl: String) : PhotoUploadState()
    data class Error(val message: String) : PhotoUploadState()
}

@HiltViewModel
class CheckInViewModel @Inject constructor(
    private val checkInRepository: CheckInRepository,
    private val recommendationRepository: RecommendationRepository,
    private val bettingPlanRepository: BettingPlanRepository,
    private val tokenManager: TokenManager
) : ViewModel() {

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.CHINA)

    private val _checkInState = MutableLiveData<CheckInState>(CheckInState.Idle)
    val checkInState: LiveData<CheckInState> = _checkInState

    private val _photoUploadState = MutableLiveData<PhotoUploadState>(PhotoUploadState.Idle)
    val photoUploadState: LiveData<PhotoUploadState> = _photoUploadState

    fun createCheckIn(
        planId: String,
        weight: String,
        note: String?,
        photoPath: String? = null
    ) {
        val weightDouble = weight.toDoubleOrNull()
        if (weightDouble == null || weightDouble < 30 || weightDouble > 300) {
            _checkInState.value = CheckInState.Error("体重必须在 30-300kg 之间")
            return
        }
    
        viewModelScope.launch {
            _checkInState.value = CheckInState.Loading

            val userId = tokenManager.getUserId()
            if (userId == null) {
                _checkInState.value = CheckInState.Error("请先登录")
                return@launch
            }
    
            val checkInData = CheckInData(
                userId = userId,
                planId = planId,
                weight = weightDouble,
                checkInDate = Date(),
                note = note
            )
    
            when (val result = checkInRepository.createCheckIn(checkInData)) {
                is NetworkResult.Success -> {
                    finishCheckIn(result.data, photoPath)
                }
                is NetworkResult.Error -> {
                    _checkInState.value = CheckInState.Error(
                        result.exception.message ?: "打卡失败"
                    )
                }
                is NetworkResult.Loading -> {}
            }
        }
    }

    private suspend fun finishCheckIn(checkIn: CheckIn, photoPath: String?) {
        if (photoPath != null && checkIn.id.startsWith("offline-")) {
            _photoUploadState.value = PhotoUploadState.Error("当前无网络，照片将在联网后重新选择并上传")
        } else if (photoPath != null) {
            _photoUploadState.value = PhotoUploadState.Loading
            when (val uploadResult = checkInRepository.uploadPhoto(checkIn.id, photoPath)) {
                is NetworkResult.Success -> {
                    _photoUploadState.value = PhotoUploadState.Success(
                        uploadResult.data.photoUrl.orEmpty()
                    )
                }
                is NetworkResult.Error -> {
                    _photoUploadState.value = PhotoUploadState.Error(
                        uploadResult.exception.message ?: "照片上传失败"
                    )
                }
                is NetworkResult.Loading -> Unit
            }
        }
        _checkInState.value = CheckInState.Success(checkIn)
        recommendationRepository.refreshAndCacheRecommendationAsync()
    }
        
    fun createCheckInForAllPlans(
        weight: String,
        note: String?,
        photoPath: String? = null
    ) {
        val weightDouble = weight.toDoubleOrNull()
        if (weightDouble == null || weightDouble < 30 || weightDouble > 300) {
            _checkInState.value = CheckInState.Error("体重必须在 30-300kg 之间")
            return
        }
    
        viewModelScope.launch {
            _checkInState.value = CheckInState.Loading
    
            val userId = tokenManager.getUserId()
            if (userId == null) {
                _checkInState.value = CheckInState.Error("请先登录")
                return@launch
            }
                
            when (val plansResult = bettingPlanRepository.getUserPlans(userId, "active", forceRefresh = true)) {
                is NetworkResult.Success -> {
                    val activePlans = plansResult.data
                    if (activePlans.isEmpty()) {
                        _checkInState.value = CheckInState.Error("没有进行中的计划")
                        return@launch
                    }
    
                    var successCount = 0
                    var failCount = 0
                    var photoFailCount = 0
                    var lastSuccessCheckIn: CheckIn? = null
    
                    for (plan in activePlans) {
                        val checkInData = CheckInData(
                            userId = userId,
                            planId = plan.id,
                            weight = weightDouble,
                            checkInDate = Date(),
                            note = note
                        )
    
                        when (val result = checkInRepository.createCheckIn(checkInData)) {
                            is NetworkResult.Success -> {
                                successCount++
                                lastSuccessCheckIn = result.data
                                if (photoPath != null) {
                                    when (val uploadResult = checkInRepository.uploadPhoto(result.data.id, photoPath)) {
                                        is NetworkResult.Success -> Unit
                                        is NetworkResult.Error -> photoFailCount++
                                        is NetworkResult.Loading -> Unit
                                    }
                                }
                            }
                            is NetworkResult.Error -> {
                                failCount++
                            }
                            else -> {}
                        }
                    }
    
                    if (lastSuccessCheckIn != null) {
                        if (photoPath != null) {
                            _photoUploadState.value = if (photoFailCount == 0) {
                                PhotoUploadState.Success("uploaded")
                            } else {
                                PhotoUploadState.Error("有 $photoFailCount 个计划的照片上传失败")
                            }
                        }
                        _checkInState.value = CheckInState.Success(lastSuccessCheckIn)
                        recommendationRepository.refreshAndCacheRecommendationAsync()
                    } else {
                        _checkInState.value = CheckInState.Error("所有计划打卡失败")
                    }
                }
                is NetworkResult.Error -> {
                    _checkInState.value = CheckInState.Error(
                        plansResult.exception.message ?: "获取计划列表失败"
                    )
                }
                else -> {}
            }
        }
    }
}
