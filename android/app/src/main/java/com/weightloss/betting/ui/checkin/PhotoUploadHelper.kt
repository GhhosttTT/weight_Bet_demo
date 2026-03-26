package com.weightloss.betting.ui.checkin

import android.Manifest
import android.app.Activity
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.net.Uri
import android.provider.MediaStore
import androidx.activity.result.ActivityResultLauncher
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import java.io.File
import java.io.FileOutputStream
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.*

class PhotoUploadHelper(
    private val context: Context,
    private val onPhotoSelected: (String) -> Unit
) {
    
    private var currentPhotoPath: String? = null
    
    fun hasPermissions(): Boolean {
        return ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.CAMERA
        ) == PackageManager.PERMISSION_GRANTED
    }
    
    fun createImageFile(): File {
        val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
        val storageDir = context.getExternalFilesDir(null)
        return File.createTempFile(
            "JPEG_${timeStamp}_",
            ".jpg",
            storageDir
        ).apply {
            currentPhotoPath = absolutePath
        }
    }
    
    fun getCameraIntent(): Intent {
        val photoFile = createImageFile()
        val photoUri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            photoFile
        )
        
        return Intent(MediaStore.ACTION_IMAGE_CAPTURE).apply {
            putExtra(MediaStore.EXTRA_OUTPUT, photoUri)
        }
    }
    
    fun getGalleryIntent(): Intent {
        return Intent(Intent.ACTION_PICK, MediaStore.Images.Media.EXTERNAL_CONTENT_URI)
    }
    
    fun handleCameraResult() {
        currentPhotoPath?.let { path ->
            val compressedPath = compressImage(path)
            onPhotoSelected(compressedPath)
        }
    }
    
    fun handleGalleryResult(data: Intent?) {
        data?.data?.let { uri ->
            val path = getRealPathFromUri(uri)
            path?.let {
                val compressedPath = compressImage(it)
                onPhotoSelected(compressedPath)
            }
        }
    }
    
    private fun compressImage(imagePath: String): String {
        val bitmap = BitmapFactory.decodeFile(imagePath)
        
        // Calculate scale to reduce image size
        val maxSize = 1024
        val scale = if (bitmap.width > bitmap.height) {
            maxSize.toFloat() / bitmap.width
        } else {
            maxSize.toFloat() / bitmap.height
        }
        
        val scaledBitmap = if (scale < 1) {
            Bitmap.createScaledBitmap(
                bitmap,
                (bitmap.width * scale).toInt(),
                (bitmap.height * scale).toInt(),
                true
            )
        } else {
            bitmap
        }
        
        // Save compressed image
        val compressedFile = File(context.cacheDir, "compressed_${System.currentTimeMillis()}.jpg")
        FileOutputStream(compressedFile).use { out ->
            scaledBitmap.compress(Bitmap.CompressFormat.JPEG, 80, out)
        }
        
        bitmap.recycle()
        if (scaledBitmap != bitmap) {
            scaledBitmap.recycle()
        }
        
        return compressedFile.absolutePath
    }
    
    private fun getRealPathFromUri(uri: Uri): String? {
        val projection = arrayOf(MediaStore.Images.Media.DATA)
        context.contentResolver.query(uri, projection, null, null, null)?.use { cursor ->
            val columnIndex = cursor.getColumnIndexOrThrow(MediaStore.Images.Media.DATA)
            cursor.moveToFirst()
            return cursor.getString(columnIndex)
        }
        return null
    }
}
