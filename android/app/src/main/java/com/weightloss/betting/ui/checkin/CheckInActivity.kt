package com.weightloss.betting.ui.checkin

import android.Manifest
import android.app.Activity
import android.content.Intent
import android.graphics.BitmapFactory
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import com.weightloss.betting.databinding.ActivityCheckInBinding
import com.weightloss.betting.ui.base.BaseActivity
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class CheckInActivity : BaseActivity() {
    
    private lateinit var binding: ActivityCheckInBinding
    private val viewModel: CheckInViewModel by viewModels()
    
    private var planId: String? = null
    private var selectedPhotoPath: String? = null
    private lateinit var photoUploadHelper: PhotoUploadHelper

    private val cameraLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            photoUploadHelper.handleCameraResult()
        }
    }

    private val galleryLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) {
            photoUploadHelper.handleGalleryResult(result.data)
        }
    }

    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) cameraLauncher.launch(photoUploadHelper.getCameraIntent())
        else Toast.makeText(this, "需要相机权限才能拍照", Toast.LENGTH_SHORT).show()
    }
        
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCheckInBinding.inflate(layoutInflater)
        setContentView(binding.root)
            
        planId = intent.getStringExtra("PLAN_ID")

        photoUploadHelper = PhotoUploadHelper(this) { path ->
            selectedPhotoPath = path
            binding.ivPhoto.setImageBitmap(BitmapFactory.decodeFile(path))
            binding.ivPhoto.visibility = View.VISIBLE
            Toast.makeText(this, "照片已选择，提交打卡后上传", Toast.LENGTH_SHORT).show()
        }
            
        setupToolbar()
        setupObservers()
        setupListeners()
    }
    
    private fun setupToolbar() {
        setSupportActionBar(binding.toolbar)
        supportActionBar?.setDisplayHomeAsUpEnabled(true)
    }
    
    private fun setupObservers() {
        viewModel.checkInState.observe(this) { state ->
            when (state) {
                is CheckInState.Idle -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSubmit.isEnabled = true
                }
                is CheckInState.Loading -> {
                    binding.progressBar.visibility = View.VISIBLE
                    binding.btnSubmit.isEnabled = false
                }
                is CheckInState.Success -> {
                    binding.progressBar.visibility = View.GONE
                    Toast.makeText(this, "打卡成功", Toast.LENGTH_SHORT).show()
                    finish()
                }
                is CheckInState.Error -> {
                    binding.progressBar.visibility = View.GONE
                    binding.btnSubmit.isEnabled = true
                    Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
                }
            }
        }

        viewModel.photoUploadState.observe(this) { state ->
            if (state is PhotoUploadState.Error) {
                Toast.makeText(this, state.message, Toast.LENGTH_LONG).show()
            }
        }
    }
    
    private fun setupListeners() {
        binding.btnSelectPhoto.setOnClickListener {
            showPhotoSourceDialog()
        }
        binding.btnSubmit.setOnClickListener {
            submitCheckIn()
        }
    }

    private fun showPhotoSourceDialog() {
        androidx.appcompat.app.AlertDialog.Builder(this)
            .setTitle("选择照片来源")
            .setItems(arrayOf("拍照", "从相册选择")) { _, which ->
                if (which == 0) {
                    if (photoUploadHelper.hasPermissions()) {
                        cameraLauncher.launch(photoUploadHelper.getCameraIntent())
                    } else {
                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                    }
                } else {
                    galleryLauncher.launch(photoUploadHelper.getGalleryIntent())
                }
            }
            .setNegativeButton("取消", null)
            .show()
    }
    
    private fun submitCheckIn() {
        val weight = binding.etWeight.text.toString()
        val note = binding.etNote.text.toString().takeIf { it.isNotBlank() }
        
        if (weight.isBlank()) {
            Toast.makeText(this, "请输入体重", Toast.LENGTH_SHORT).show()
            return
        }
        
        // 如果没有传入 planId，表示对所有计划打卡
        if (planId == null) {
            viewModel.createCheckInForAllPlans(weight, note, selectedPhotoPath)
        } else {
            viewModel.createCheckIn(planId!!, weight, note, selectedPhotoPath)
        }
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
