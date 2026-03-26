package com.weightloss.betting.ui.checkin

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.CheckIn
import com.weightloss.betting.data.model.CreateCheckInRequest
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.CheckInData
import com.weightloss.betting.data.repository.CheckInRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import java.text.SimpleDateFormat
import java.util.*
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
    private val checkInRepository: CheckInRepository
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
        // Validate weight
        val weightDouble = weight.toDoubleOrNull()
        if (weightDouble == null || weightDouble < 30 || weightDouble > 300) {
            _checkInState.value = CheckInState.Error("体重必须在30-300kg之间")
            return
        }
        
        viewModelScope.launch {
            _checkInState.value = CheckInState.Loading
            
            val checkInData = CheckInData(
                userId = "current_user_id", // TODO: Get from auth
                planId = planId,
                weight = weightDouble,
                checkInDate = Date(),
                note = note
            )
            
            when (val result = checkInRepository.createCheckIn(checkInData)) {
                is NetworkResult.Success -> {
                    _checkInState.value = CheckInState.Success(result.data)
                }
                is NetworkResult.Error -> {
                    _checkInState.value = CheckInState.Error(
                        result.exception.message ?: "打卡失败"
                    )
                }
                is NetworkResult.Loading -> {
                    // Already handled
                }
            }
        }
    }
}
