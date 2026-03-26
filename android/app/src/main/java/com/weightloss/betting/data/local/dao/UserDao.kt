package com.weightloss.betting.data.local.dao

import androidx.room.*
import com.weightloss.betting.data.local.entity.UserEntity
import kotlinx.coroutines.flow.Flow

/**
 * 用户 DAO
 */
@Dao
interface UserDao {
    
    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserById(userId: String): Flow<UserEntity?>
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertUser(user: UserEntity)
    
    @Update
    suspend fun updateUser(user: UserEntity)
    
    @Delete
    suspend fun deleteUser(user: UserEntity)
    
    @Query("DELETE FROM users")
    suspend fun deleteAll()
}
