package com.weightloss.betting.ui.checkin

import android.Manifest
import android.content.pm.PackageManager
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.activity.viewModels
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import coil.load
import com.weightloss.betting.databinding.ActivityCheckInBinding
import dagger.hilt.android.AndroidEntryPoint
import java.io.File

@AndroidEntryPoint
class CheckInActivity : AppCompatActivity() {
    
    private lateinit var binding: ActivityCheckInBinding
    private val viewModel: CheckInViewModel by viewModels()
    
    private lateinit var photoUploadHelper: PhotoUploadHelper
    private var selectedPhotoPath: String? = null
    private var planId: String? = null
    
    private val cameraLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            photoUploadHelper.handleCameraResult()
        }
    }
    
    private val galleryLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            photoUploadHelper.handleGalleryResult(result.data)
        }
    }
    
    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) {
            showPhotoSourceDialog()
        } else {
            Toast.makeText(this, "需要相机和存储权限才能上传照片", Toast.LENGTH_SHORT).show()
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityCheckInBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        planId = intent.getStringExtra("PLAN_ID")
        
        if (planId == null) {
            Toast.makeText(this, "计划ID无效", Toast.LENGTH_SHORT).show()
            finish()
            return
        }
        
        photoUploadHelper = PhotoUploadHelper(this) { photoPath ->
            selectedPhotoPath = photoPath
            binding.ivPhoto.load(File(photoPath))
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
    }
    
    private fun setupListeners() {
        binding.btnSelectPhoto.setOnClickListener {
            checkPermissionsAndSelectPhoto()
        }
        
        binding.btnSubmit.setOnClickListener {
            submitCheckIn()
        }
    }
    
    private fun checkPermissionsAndSelectPhoto() {
        val permissions = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.READ_EXTERNAL_STORAGE
        )
        
        val allGranted = permissions.all {
            ContextCompat.checkSelfPermission(this, it) == PackageManager.PERMISSION_GRANTED
        }
        
        if (allGranted) {
            showPhotoSourceDialog()
        } else {
            permissionLauncher.launch(permissions)
        }
    }
    
    private fun showPhotoSourceDialog() {
        AlertDialog.Builder(this)
            .setTitle("选择照片来源")
            .setItems(arrayOf("拍照", "从相册选择")) { _, which ->
                when (which) {
                    0 -> cameraLauncher.launch(photoUploadHelper.getCameraIntent())
                    1 -> galleryLauncher.launch(photoUploadHelper.getGalleryIntent())
                }
            }
            .show()
    }
    
    private fun submitCheckIn() {
        val weight = binding.etWeight.text.toString()
        val note = binding.etNote.text.toString().takeIf { it.isNotBlank() }
        
        if (weight.isBlank()) {
            Toast.makeText(this, "请输入体重", Toast.LENGTH_SHORT).show()
            return
        }
        
        viewModel.createCheckIn(planId!!, weight, note)
    }
    
    override fun onSupportNavigateUp(): Boolean {
        finish()
        return true
    }
}
