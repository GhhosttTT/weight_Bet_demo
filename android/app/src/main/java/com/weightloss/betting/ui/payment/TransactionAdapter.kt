package com.weightloss.betting.ui.payment

import android.view.LayoutInflater
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.weightloss.betting.data.model.Transaction
import com.weightloss.betting.databinding.ItemTransactionBinding
import java.text.SimpleDateFormat
import java.util.*

class TransactionAdapter : ListAdapter<Transaction, TransactionAdapter.TransactionViewHolder>(TransactionDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): TransactionViewHolder {
        val binding = ItemTransactionBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return TransactionViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: TransactionViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    class TransactionViewHolder(
        private val binding: ItemTransactionBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        private val dateFormat = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault())
        
        fun bind(transaction: Transaction) {
            binding.tvType.text = when (transaction.type) {
                "freeze" -> "冻结"
                "unfreeze" -> "解冻"
                "transfer" -> "转账"
                "withdraw" -> "提现"
                "refund" -> "退款"
                "charge" -> "充值"
                else -> transaction.type
            }
            
            binding.tvDate.text = dateFormat.format(transaction.createdAt)
            
            binding.tvStatus.text = when (transaction.status) {
                "pending" -> "处理中"
                "completed" -> "已完成"
                "failed" -> "失败"
                else -> transaction.status
            }
            
            val amountText = if (transaction.type in listOf("charge", "unfreeze", "refund")) {
                "+¥${transaction.amount}"
            } else {
                "-¥${transaction.amount}"
            }
            binding.tvAmount.text = amountText
        }
    }
    
    class TransactionDiffCallback : DiffUtil.ItemCallback<Transaction>() {
        override fun areItemsTheSame(oldItem: Transaction, newItem: Transaction): Boolean {
            return oldItem.id == newItem.id
        }
        
        override fun areContentsTheSame(oldItem: Transaction, newItem: Transaction): Boolean {
            return oldItem == newItem
        }
    }
}
