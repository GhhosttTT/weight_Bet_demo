package com.weightloss.betting.ui.social

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.weightloss.betting.data.model.Badge
import com.weightloss.betting.databinding.ItemBadgeBinding
import java.text.SimpleDateFormat
import java.util.*

class BadgesAdapter : ListAdapter<Badge, BadgesAdapter.BadgeViewHolder>(BadgeDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): BadgeViewHolder {
        val binding = ItemBadgeBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return BadgeViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: BadgeViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class BadgeViewHolder(
        private val binding: ItemBadgeBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.getDefault())
        
        fun bind(badge: Badge) {
            binding.tvBadgeName.text = badge.name
            binding.tvBadgeDescription.text = badge.description
            binding.tvAwardedAt.text = "获得于: ${dateFormat.format(badge.awardedAt)}"
            
            // 根据勋章名称显示不同的图标
            binding.tvBadgeIcon.text = when (badge.name) {
                "初次挑战" -> "🎯"
                "坚持一周" -> "📅"
                "坚持一月" -> "📆"
                "减重达人" -> "⚖️"
                "常胜将军" -> "👑"
                else -> "🏆"
            }
        }
    }
    
    class BadgeDiffCallback : DiffUtil.ItemCallback<Badge>() {
        override fun areItemsTheSame(oldItem: Badge, newItem: Badge): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: Badge, newItem: Badge): Boolean {
            return oldItem == newItem
        }
    }
}
