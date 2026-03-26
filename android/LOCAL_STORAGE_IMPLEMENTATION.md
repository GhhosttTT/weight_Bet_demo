# Android 本地存储实现总结

## 任务概述

实现了 Android 客户端的完整本地存储功能,包括 Room 数据库、本地缓存策略和离线队列支持。

## 已完成的功能

### 1. Room 数据库配置 (任务 19.1)

#### 数据实体 (Entity)

1. **UserEntity** - 用户本地实体
   - 存储用户基本信息 (id, email, nickname, gender, age, height, weight)
   - 支持日期类型转换

2. **BettingPlanEntity** - 对赌计划本地实体
   - 存储计划信息 (id, creatorId, participantId, status, betAmount, dates)
   - 存储双方目标体重数据
   - 支持计划状态和激活时间

3. **CheckInEntity** - 打卡记录本地实体
   - 存储打卡数据 (id, userId, planId, weight, date)
   - 支持照片 URL 和备注
   - 记录审核状态

4. **OfflineCheckInEntity** - 离线打卡队列实体 (新增)
   - 存储离线状态下创建的打卡记录
   - 跟踪同步状态 (pending, syncing, synced, failed)
   - 记录同步尝试次数和错误信息

#### DAO 接口

1. **UserDao** - 用户数据访问对象
   - 查询、插入、更新、删除用户
   - 支持 Flow 响应式查询

2. **BettingPlanDao** - 对赌计划数据访问对象
   - 按 ID 查询计划
   - 查询用户的所有计划
   - 按状态筛选计划
   - 批量插入和更新

3. **CheckInDao** - 打卡记录数据访问对象
   - 按计划查询打卡历史
   - 按用户和计划查询
   - 批量插入打卡记录

4. **OfflineCheckInDao** - 离线打卡队列数据访问对象 (新增)
   - 查询待同步的打卡记录
   - 观察待同步数量
   - 更新同步状态
   - 删除已同步记录

#### 数据库配置

- **AppDatabase** - Room 数据库主类
  - 版本: 2 (新增离线队列表)
  - 包含 4 个实体表
  - 配置类型转换器 (Date ↔ Long)
  - 使用 fallbackToDestructiveMigration 策略

- **Converters** - 类型转换器
  - Date 与 Long 之间的转换

### 2. 本地缓存策略 (任务 19.2)

#### CacheManager - 缓存管理器

统一管理所有本地缓存操作:

**用户信息缓存**:
- `cacheUser()` - 缓存用户信息
- `getCachedUser()` - 获取缓存的用户信息 (Flow)
- `clearUserCache()` - 清除用户缓存

**对赌计划缓存**:
- `cachePlan()` - 缓存单个计划
- `cachePlans()` - 批量缓存计划
- `getCachedPlan()` - 获取缓存的计划 (Flow)
- `getCachedUserPlans()` - 获取用户的所有缓存计划 (Flow)
- `getCachedUserPlansByStatus()` - 按状态获取缓存计划 (Flow)
- `clearPlanCache()` - 清除计划缓存

**打卡历史缓存**:
- `cacheCheckIn()` - 缓存单个打卡记录
- `cacheCheckIns()` - 批量缓存打卡记录
- `getCachedCheckIns()` - 获取计划的缓存打卡历史 (Flow)
- `getCachedUserCheckIns()` - 获取用户在计划中的缓存打卡历史 (Flow)
- `clearCheckInCache()` - 清除打卡缓存
- `clearCheckInCacheByPlan()` - 清除指定计划的打卡缓存

**特点**:
- 使用 Flow 提供响应式数据流
- 自动转换 Entity 和 Model 之间的数据
- 支持批量操作提高性能

### 3. 离线队列 (任务 19.3)

#### OfflineSyncService - 离线同步服务

管理离线打卡队列和自动同步:

**网络监听**:
- 使用 ConnectivityManager 监听网络状态
- 网络恢复时自动触发同步
- 检查网络可用性

**离线队列管理**:
- `addOfflineCheckIn()` - 添加离线打卡到队列
- `observePendingCount()` - 观察待同步数量 (Flow)
- `getOfflineCheckIns()` - 获取用户的离线打卡记录 (Flow)
- `clearOfflineQueue()` - 清除所有离线记录

**自动同步**:
- `syncPendingCheckIns()` - 同步所有待同步的打卡记录
- 按创建时间顺序同步
- 更新同步状态 (pending → syncing → synced/failed)
- 记录同步尝试次数 (最多 3 次)
- 同步成功后自动缓存到本地
- 自动清理已同步的记录

**手动同步**:
- `manualSync()` - 手动触发同步
- 返回同步结果 (成功数、失败数、消息)

**冲突处理**:
- 同步失败时保留在队列中
- 记录错误信息供用户查看
- 超过 3 次失败后标记为 failed 状态

### 4. Repository 层集成

#### UserRepository - 用户仓库

集成缓存策略:
- `getUserProfile()` - 优先从缓存读取,支持强制刷新
- `observeCachedUser()` - 观察缓存的用户信息
- `updateUserProfile()` - 更新后自动缓存
- `clearCache()` - 清除缓存

#### BettingPlanRepository - 对赌计划仓库

集成缓存策略:
- `createPlan()` - 创建后自动缓存
- `getPlanDetails()` - 优先从缓存读取,支持强制刷新
- `observeCachedPlan()` - 观察缓存的计划
- `getUserPlans()` - 优先从缓存读取,支持按状态筛选
- `observeCachedUserPlans()` - 观察用户的缓存计划
- `acceptPlan()` - 接受后自动更新缓存
- `clearCache()` - 清除缓存

#### CheckInRepository - 打卡仓库

集成缓存和离线支持:
- `createCheckIn()` - 支持离线模式
  - 在线: 直接提交到服务器并缓存
  - 离线: 添加到离线队列,返回临时 ID
- `getCheckInHistory()` - 优先从缓存读取,支持强制刷新
- `observeCachedCheckIns()` - 观察缓存的打卡历史
- `observePendingSyncCount()` - 观察待同步数量
- `syncOfflineCheckIns()` - 手动触发同步
- `clearCache()` - 清除缓存

**离线打卡流程**:
1. 检查网络连接
2. 如果离线,添加到离线队列
3. 返回临时 ID (offline_xxx)
4. 网络恢复时自动同步
5. 同步成功后缓存到本地

### 5. 依赖注入配置

#### DatabaseModule

提供所有数据库相关依赖:
- AppDatabase 实例
- UserDao
- BettingPlanDao
- CheckInDao
- OfflineCheckInDao

所有依赖都是 Singleton 单例。

## 技术特点

1. **响应式数据流**: 使用 Flow 提供实时数据更新
2. **离线优先**: 离线状态下仍可创建打卡记录
3. **自动同步**: 网络恢复时自动同步离线数据
4. **缓存策略**: 优先从缓存读取,减少网络请求
5. **冲突处理**: 同步失败时保留数据并记录错误
6. **类型安全**: 使用 Kotlin 协程和类型安全的 API
7. **依赖注入**: 使用 Hilt 管理依赖,易于测试

## 使用示例

### 示例 1: 缓存用户信息

```kotlin
class ProfileViewModel @Inject constructor(
    private val userRepository: UserRepository
) : ViewModel() {
    
    // 观察缓存的用户信息
    val user: Flow<User?> = userRepository.observeCachedUser(userId)
    
    fun loadUserProfile(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            when (val result = userRepository.getUserProfile(userId, forceRefresh)) {
                is NetworkResult.Success -> {
                    // 用户信息已自动缓存
                }
                is NetworkResult.Error -> {
                    // 如果有缓存,仍可显示缓存数据
                }
                is NetworkResult.Loading -> {
                    // 显示加载状态
                }
            }
        }
    }
}
```

### 示例 2: 离线打卡

```kotlin
class CheckInViewModel @Inject constructor(
    private val checkInRepository: CheckInRepository
) : ViewModel() {
    
    // 观察待同步数量
    val pendingSyncCount: Flow<Int> = checkInRepository.observePendingSyncCount()
    
    fun checkIn(weight: Double, note: String?) {
        viewModelScope.launch {
            val data = CheckInData(
                userId = currentUserId,
                planId = currentPlanId,
                weight = weight,
                checkInDate = Date(),
                note = note
            )
            
            when (val result = checkInRepository.createCheckIn(data)) {
                is NetworkResult.Success -> {
                    if (result.data.id.startsWith("offline_")) {
                        // 离线打卡成功,等待同步
                        showMessage("打卡已保存,将在网络恢复时自动同步")
                    } else {
                        // 在线打卡成功
                        showMessage("打卡成功")
                    }
                }
                is NetworkResult.Error -> {
                    showError(result.exception.message)
                }
                is NetworkResult.Loading -> {
                    // 显示加载状态
                }
            }
        }
    }
    
    fun manualSync() {
        viewModelScope.launch {
            val result = checkInRepository.syncOfflineCheckIns()
            showMessage(result.message)
        }
    }
}
```

### 示例 3: 缓存计划列表

```kotlin
class PlanListViewModel @Inject constructor(
    private val bettingPlanRepository: BettingPlanRepository
) : ViewModel() {
    
    // 观察缓存的活跃计划
    val activePlans: Flow<List<BettingPlan>> = 
        bettingPlanRepository.observeCachedUserPlans(userId, "active")
    
    fun loadPlans(forceRefresh: Boolean = false) {
        viewModelScope.launch {
            when (val result = bettingPlanRepository.getUserPlans(
                userId = userId,
                status = "active",
                forceRefresh = forceRefresh
            )) {
                is NetworkResult.Success -> {
                    // 计划列表已自动缓存
                }
                is NetworkResult.Error -> {
                    // 如果有缓存,仍可显示缓存数据
                }
                is NetworkResult.Loading -> {
                    // 显示加载状态
                }
            }
        }
    }
}
```

## 文件结构

```
android/app/src/main/java/com/weightloss/betting/
├── data/
│   ├── local/
│   │   ├── dao/
│   │   │   ├── UserDao.kt                    # 用户 DAO
│   │   │   ├── BettingPlanDao.kt             # 对赌计划 DAO
│   │   │   ├── CheckInDao.kt                 # 打卡记录 DAO
│   │   │   └── OfflineCheckInDao.kt          # 离线打卡队列 DAO (新增)
│   │   ├── entity/
│   │   │   ├── UserEntity.kt                 # 用户实体
│   │   │   ├── BettingPlanEntity.kt          # 对赌计划实体
│   │   │   ├── CheckInEntity.kt              # 打卡记录实体
│   │   │   └── OfflineCheckInEntity.kt       # 离线打卡队列实体 (新增)
│   │   ├── AppDatabase.kt                    # 数据库配置 (已更新)
│   │   ├── Converters.kt                     # 类型转换器
│   │   ├── CacheManager.kt                   # 缓存管理器 (新增)
│   │   └── OfflineSyncService.kt             # 离线同步服务 (新增)
│   └── repository/
│       ├── UserRepository.kt                 # 用户仓库 (已更新)
│       ├── BettingPlanRepository.kt          # 对赌计划仓库 (已更新)
│       └── CheckInRepository.kt              # 打卡仓库 (已更新)
└── di/
    └── DatabaseModule.kt                     # 数据库模块 (已更新)
```

## 数据库迁移

数据库版本从 1 升级到 2:
- 新增 `offline_check_ins` 表
- 使用 `fallbackToDestructiveMigration()` 策略 (开发阶段)
- 生产环境建议实现正式的迁移策略

## 性能优化

1. **批量操作**: 支持批量插入计划和打卡记录
2. **索引优化**: 在常用查询字段上添加索引
3. **Flow 响应式**: 使用 Flow 避免不必要的查询
4. **缓存优先**: 减少网络请求,提高响应速度
5. **后台同步**: 使用协程在后台线程执行数据库操作

## 注意事项

1. **数据一致性**: 同步时以服务器数据为准
2. **错误处理**: 同步失败时保留数据并记录错误
3. **内存管理**: 使用 Flow 避免内存泄漏
4. **线程安全**: 所有数据库操作在 IO 线程执行
5. **网络监听**: 记得在适当时机释放网络监听器

## 下一步工作

本地存储已完成,接下来可以:
1. 实现 ViewModel 层
2. 实现 UI 层 (Activity/Fragment/Compose)
3. 编写单元测试 (可选)
4. 实现数据库迁移策略
5. 优化同步策略 (增量同步、冲突解决)

## 总结

Android 本地存储已完整实现,包括:
- ✅ Room 数据库配置 (4 个实体, 4 个 DAO)
- ✅ 本地缓存策略 (用户、计划、打卡)
- ✅ 离线队列 (离线打卡、自动同步)
- ✅ Repository 层集成 (缓存优先、离线支持)
- ✅ 依赖注入配置

本地存储提供了完整的离线支持和缓存策略,为用户提供流畅的使用体验,即使在网络不稳定的情况下也能正常使用核心功能。
