package com.weightloss.betting.ui.profile

import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.viewModels
import com.stripe.android.paymentsheet.PaymentSheet
import com.stripe.android.paymentsheet.PaymentSheetResult
import com.weightloss.betting.databinding.ActivityPaymentMethodBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class PaymentMethodActivity : BaseActivity() {
    private lateinit var binding: ActivityPaymentMethodBinding
    private val viewModel: PaymentMethodViewModel by viewModels()
    private lateinit var paymentSheet: PaymentSheet

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityPaymentMethodBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
        paymentSheet = PaymentSheet(this, ::onPaymentSheetResult)

        viewModel.state.observe(this) { state ->
            binding.progressBar.visibility = if (state is PaymentMethodState.Loading) View.VISIBLE else View.GONE
            binding.btnSetup.isEnabled = state !is PaymentMethodState.Loading
            when (state) {
                is PaymentMethodState.SetupIntentReady -> paymentSheet.presentWithSetupIntent(
                    state.clientSecret,
                    PaymentSheet.Configuration("BetFit")
                )
                is PaymentMethodState.Success -> {
                    Toast.makeText(this, "支付方式设置已完成", Toast.LENGTH_LONG).show()
                    finish()
                }
                is PaymentMethodState.Error -> Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                else -> Unit
            }
        }

        binding.btnSetup.setOnClickListener { viewModel.createSetupIntent() }
    }

    private fun onPaymentSheetResult(result: PaymentSheetResult) {
        when (result) {
            is PaymentSheetResult.Completed -> viewModel.setupCompleted()
            is PaymentSheetResult.Canceled -> viewModel.setupCanceled()
            is PaymentSheetResult.Failed -> viewModel.setupFailed(
                result.error.localizedMessage ?: "支付方式设置失败"
            )
        }
    }

    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
