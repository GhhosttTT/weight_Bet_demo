package com.weightloss.betting.ui.social

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.weightloss.betting.data.model.Comment
import com.weightloss.betting.data.remote.NetworkResult
import com.weightloss.betting.data.repository.SocialRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.launch
import javax.inject.Inject

sealed class CommentsState {
    object Loading : CommentsState()
    data class Ready(val comments: List<Comment>) : CommentsState()
    data class Posting(val comments: List<Comment>) : CommentsState()
    data class Error(val message: String, val comments: List<Comment> = emptyList()) : CommentsState()
}

@HiltViewModel
class CommentsViewModel @Inject constructor(
    private val repository: SocialRepository
) : ViewModel() {
    private val _state = MutableLiveData<CommentsState>()
    val state: LiveData<CommentsState> = _state

    fun load(planId: String) {
        viewModelScope.launch {
            _state.value = CommentsState.Loading
            when (val result = repository.getComments(planId)) {
                is NetworkResult.Success -> _state.value = CommentsState.Ready(result.data)
                is NetworkResult.Error -> _state.value = CommentsState.Error(
                    result.exception.message ?: "加载评论失败"
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }

    fun post(planId: String, content: String, current: List<Comment>) {
        viewModelScope.launch {
            _state.value = CommentsState.Posting(current)
            when (val result = repository.postComment(planId, content)) {
                is NetworkResult.Success -> _state.value = CommentsState.Ready(listOf(result.data) + current)
                is NetworkResult.Error -> _state.value = CommentsState.Error(
                    result.exception.message ?: "发表评论失败", current
                )
                is NetworkResult.Loading -> Unit
            }
        }
    }
}
