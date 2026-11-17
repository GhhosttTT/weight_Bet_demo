package com.weightloss.betting.ui.profile

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.weightloss.betting.databinding.ActivityPaymentMethodBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class PaymentMethodActivity : BaseActivity() {
    private lateinit var binding: ActivityPaymentMethodBinding
    private val viewModel: PaymentMethodViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPaymentMethodBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)

        viewModel.state.observe(this) { state ->
            binding.progressBar.visibility = if (state is PaymentMethodState.Loading) View.VISIBLE else View.GONE
            binding.btnSave.isEnabled = state !is PaymentMethodState.Loading
            when (state) {
                is PaymentMethodState.Success -> {
                    Toast.makeText(this, "支付方式已绑定", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is PaymentMethodState.Error -> Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                else -> Unit
            }
        }

        binding.btnSave.setOnClickListener {
            viewModel.bind(
                binding.etCardNumber.text.toString(),
                binding.etExpiry.text.toString(),
                binding.etCvv.text.toString(),
                binding.etHolder.text.toString()
            )
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
