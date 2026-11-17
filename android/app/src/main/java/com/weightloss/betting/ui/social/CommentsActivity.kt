package com.weightloss.betting.ui.social

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import androidx.recyclerview.widget.LinearLayoutManager
import com.weightloss.betting.databinding.ActivityCommentsBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CommentsActivity : BaseActivity() {
    private lateinit var binding: ActivityCommentsBinding
    private val viewModel: CommentsViewModel by viewModels()
    private val adapter = CommentsAdapter()
    private var planId: String? = null
    private var currentComments = emptyList<com.weightloss.betting.data.model.Comment>()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCommentsBinding.inflate(layoutInflater)
        setContentView(binding.root)
        planId = intent.getStringExtra("PLAN_ID")
        if (planId.isNullOrBlank()) {
            Toast.makeText(this, "计划 ID 无效", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        binding.toolbar.setNavigationOnClickListener { finish() }
        binding.recyclerView.layoutManager = LinearLayoutManager(this)
        binding.recyclerView.adapter = adapter
        binding.btnSend.setOnClickListener { sendComment() }
        binding.btnRetry.setOnClickListener { viewModel.load(planId!!) }
        viewModel.state.observe(this) { render(it) }
        viewModel.load(planId!!)
    }

    private fun sendComment() {
        val content = binding.etComment.text?.toString()?.trim().orEmpty()
        when {
            content.isEmpty() -> Toast.makeText(this, "请输入评论内容", Toast.LENGTH_SHORT).show()
            content.length > 500 -> Toast.makeText(this, "评论内容不能超过500个字符", Toast.LENGTH_SHORT).show()
            else -> viewModel.post(planId!!, content, currentComments)
        }
    }

    private fun render(state: CommentsState) {
        when (state) {
            is CommentsState.Loading -> {
                binding.progressBar.visibility = View.VISIBLE
                binding.errorState.visibility = View.GONE
                binding.btnSend.isEnabled = false
            }
            is CommentsState.Posting -> {
                currentComments = state.comments
                adapter.submitList(state.comments)
                binding.progressBar.visibility = View.VISIBLE
                binding.btnSend.isEnabled = false
            }
            is CommentsState.Ready -> {
                currentComments = state.comments
                adapter.submitList(state.comments)
                binding.progressBar.visibility = View.GONE
                binding.btnSend.isEnabled = true
                binding.errorState.visibility = View.GONE
                binding.emptyState.visibility = if (state.comments.isEmpty()) View.VISIBLE else View.GONE
                binding.recyclerView.visibility = if (state.comments.isEmpty()) View.GONE else View.VISIBLE
                if (state.comments.isNotEmpty()) binding.etComment.text?.clear()
            }
            is CommentsState.Error -> {
                currentComments = state.comments
                adapter.submitList(state.comments)
                binding.progressBar.visibility = View.GONE
                binding.btnSend.isEnabled = true
                binding.tvError.text = state.message
                binding.errorState.visibility = View.VISIBLE
                binding.emptyState.visibility = View.GONE
                binding.recyclerView.visibility = if (state.comments.isEmpty()) View.GONE else View.VISIBLE
            }
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
