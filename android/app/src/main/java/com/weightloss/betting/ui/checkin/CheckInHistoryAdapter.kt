package com.weightloss.betting.ui.checkin

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.weightloss.betting.data.model.CheckIn
import com.weightloss.betting.databinding.ItemCheckInHistoryBinding
import java.text.SimpleDateFormat
import java.util.Locale

class CheckInHistoryAdapter : ListAdapter<CheckIn, CheckInHistoryAdapter.ViewHolder>(DiffCallback()) {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder = ViewHolder(
        ItemCheckInHistoryBinding.inflate(LayoutInflater.from(parent.context), parent, false)
    )

    override fun onBindViewHolder(holder: ViewHolder, position: Int) {
        holder.bind(getItem(position))
    }

    class ViewHolder(private val binding: ItemCheckInHistoryBinding) : RecyclerView.ViewHolder(binding.root) {
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())

        fun bind(item: CheckIn) {
            binding.tvDate.text = dateFormat.format(item.checkInDate)
            binding.tvWeight.text = String.format(Locale.CHINA, "%.1f kg", item.weight)
            binding.tvStatus.text = when (item.reviewStatus.lowercase(Locale.getDefault())) {
                "approved" -> "已审核"
                "rejected" -> "未通过"
                "pending" -> "审核中"
                else -> item.reviewStatus
            }
            binding.tvNote.text = item.note?.takeIf { it.isNotBlank() } ?: "暂无备注"
        }
    }

    private class DiffCallback : DiffUtil.ItemCallback<CheckIn>() {
        override fun areItemsTheSame(oldItem: CheckIn, newItem: CheckIn): Boolean = oldItem.id == newItem.id
        override fun areContentsTheSame(oldItem: CheckIn, newItem: CheckIn): Boolean = oldItem == newItem
    }
}
