package com.weightloss.betting.ui.social

import android.graphics.Color
import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.weightloss.betting.data.model.LeaderboardEntry
import com.weightloss.betting.databinding.ItemLeaderboardBinding

class LeaderboardAdapter(
    private val type: String
) : ListAdapter<LeaderboardEntry, LeaderboardAdapter.LeaderboardViewHolder>(LeaderboardDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): LeaderboardViewHolder {
        val binding = ItemLeaderboardBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return LeaderboardViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: LeaderboardViewHolder, position: Int) {
        holder.bind(getItem(position), type)
    }
    
    class LeaderboardViewHolder(
        private val binding: ItemLeaderboardBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        fun bind(entry: LeaderboardEntry, type: String) {
            binding.tvRank.text = entry.rank.toString()
            binding.tvNickname.text = entry.nickname
            
            // 根据排名设置背景颜色
            val rankColor = when (entry.rank) {
                1 -> Color.parseColor("#FFD700") // 金色
                2 -> Color.parseColor("#C0C0C0") // 银色
                3 -> Color.parseColor("#CD7F32") // 铜色
                else -> Color.parseColor("#9E9E9E") // 灰色
            }
            binding.tvRank.setBackgroundColor(rankColor)
            
            // 根据类型显示不同的值
            binding.tvValue.text = when (type) {
                "weight-loss" -> String.format("%.1f kg", entry.value)
                "check-in-streak" -> String.format("%.0f 天", entry.value)
                "win-rate" -> String.format("%.1f%%", entry.value * 100)
                else -> entry.value.toString()
            }
        }
    }
    
    class LeaderboardDiffCallback : DiffUtil.ItemCallback<LeaderboardEntry>() {
        override fun areItemsTheSame(oldItem: LeaderboardEntry, newItem: LeaderboardEntry): Boolean {
            return oldItem.userId == newItem.userId
        }
        
        override fun areContentsTheSame(oldItem: LeaderboardEntry, newItem: LeaderboardEntry): Boolean {
            return oldItem == newItem
        }
    }
}
