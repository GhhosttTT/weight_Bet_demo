package com.weightloss.betting.ui.plan

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.weightloss.betting.data.model.BettingPlan
import com.weightloss.betting.databinding.ItemBettingPlanBinding
import java.text.SimpleDateFormat
import java.util.*

class PlanAdapter(
    private val onPlanClick: (BettingPlan) -> Unit
) : ListAdapter<BettingPlan, PlanAdapter.PlanViewHolder>(PlanDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PlanViewHolder {
        val binding = ItemBettingPlanBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return PlanViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: PlanViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    inner class PlanViewHolder(
        private val binding: ItemBettingPlanBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd", Locale.getDefault())
        
        fun bind(plan: BettingPlan) {
            binding.tvStatus.text = when (plan.status) {
                "pending" -> "待接受"
                "waiting_double_check" -> "待二次确认"
                "active" -> "进行中"
                "completed" -> "已完成"
                "cancelled" -> "已取消"
                "rejected" -> "已拒绝"
                else -> plan.status
            }
            
            binding.tvBetAmount.text = "赌金: ¥${plan.betAmount}"
            binding.tvDateRange.text = "${dateFormat.format(plan.startDate)} 至 ${dateFormat.format(plan.endDate)}"
            
            val goalText = if (plan.creatorInitialWeight != null && plan.creatorTargetWeight != null) {
                "目标: ${plan.creatorInitialWeight}kg → ${plan.creatorTargetWeight}kg"
            } else {
                "目标: 待设置"
            }
            binding.tvGoal.text = goalText
            
            binding.tvDescription.text = plan.description ?: "无描述"
            
            binding.root.setOnClickListener {
                onPlanClick(plan)
            }
        }
    }
    
    class PlanDiffCallback : DiffUtil.ItemCallback<BettingPlan>() {
        override fun areItemsTheSame(oldItem: BettingPlan, newItem: BettingPlan): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: BettingPlan, newItem: BettingPlan): Boolean {
            return oldItem == newItem
        }
    }
}
