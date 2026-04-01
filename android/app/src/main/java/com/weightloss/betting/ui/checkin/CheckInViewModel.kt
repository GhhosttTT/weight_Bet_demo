package com.weightloss.betting.ui.checkin

import android.util.Log
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.CheckIn
import com.weightloss.betting.data.remote.NetworkResult
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
    private val recommendationRepository: RecommendationRepository
) : ViewModel() {

    private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.CHINA)

    private fun formatToString(date: Date): String {
        return dateFormat.format(date)
    }

    private val _checkInState = MutableLiveData<CheckInState>(CheckInState.Idle)
    val checkInState: LiveData<CheckInState> = _checkInState

    fun createCheckIn(
        planId: String,
        weight: String,
        note: String?
    ) {
        Log.d("CheckInViewModel", "createCheckIn() called")
        val weightDouble = weight.toDoubleOrNull()
        if (weightDouble == null || weightDouble < 30 || weightDouble > 300) {
            _checkInState.value = CheckInState.Error("体重必须在30-300kg之间")
            return
        }

        viewModelScope.launch {
            Log.d("CheckInViewModel", "Setting check-in state to Loading")
            _checkInState.value = CheckInState.Loading

            val checkInData = CheckInData(
                userId = "",
                planId = planId,
                weight = weightDouble,
                checkInDate = Date(),
                note = note
            )

            Log.d("CheckInViewModel", "Calling checkInRepository.createCheckIn()")
            when (val result = checkInRepository.createCheckIn(checkInData)) {
                is NetworkResult.Success -> {
                    Log.d("CheckInViewModel", "Check-in successful!")
                    Log.d("CheckInViewModel", "Setting check-in state to Success")
                    _checkInState.value = CheckInState.Success(result.data)
                    Log.d("CheckInViewModel", "Starting refreshAndCacheRecommendationAsync()")
                    recommendationRepository.refreshAndCacheRecommendationAsync()
                }
                is NetworkResult.Error -> {
                    Log.e("CheckInViewModel", "Check-in error: ${result.exception.message}")
                    _checkInState.value = CheckInState.Error(
                        result.exception.message ?: "打卡失败"
                    )
                }
                is NetworkResult.Loading -> {
                    Log.d("CheckInViewModel", "Check-in result is Loading")
                }
            }
        }
    }
}
