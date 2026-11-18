package com.weightloss.betting.di

import android.content.Context
import com.weightloss.betting.BuildConfig
import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.weightloss.betting.data.remote.ApiService
import com.weightloss.betting.data.remote.AuthInterceptor
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import dagger.hilt.android.qualifiers.ApplicationContext
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

/**
 * 网络模块 - 提供 Retrofit 和 OkHttp 依赖
 */
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    private const val TIMEOUT_SECONDS = 30L
    
    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
            .setLenient()
            .create()
    }
    
    @Provides
    @Singleton
    fun provideLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = if (BuildConfig.DEBUG) {
                HttpLoggingInterceptor.Level.BASIC
            } else {
                HttpLoggingInterceptor.Level.NONE
            }
        }
    }
    
    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        errorInterceptor: com.weightloss.betting.data.remote.ErrorInterceptor,
        retryInterceptor: com.weightloss.betting.data.remote.RetryInterceptor,
        loggingInterceptor: HttpLoggingInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(retryInterceptor)  // 重试拦截器放在最前面
            .addInterceptor(authInterceptor)
            .addInterceptor(errorInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        gson: Gson,
        @ApplicationContext context: Context
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(context.getString(com.weightloss.betting.R.string.api_base_url))
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
    
    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
