# 移动端性能测试指南

## Android 性能测试

### 1. 网络请求优化测试

**测试工具**: Android Profiler

**测试步骤**:
1. 打开 Android Studio
2. 运行应用并连接设备
3. 打开 Profiler 窗口
4. 选择 Network 标签
5. 执行各种操作并观察网络请求

**优化检查点**:
- [ ] 请求是否合并 (批量请求)
- [ ] 是否使用 HTTP/2
- [ ] 是否启用响应压缩
- [ ] 是否有不必要的重复请求
- [ ] 图片是否压缩

**性能指标**:
- 平均请求时间 < 500ms
- 数据传输量 < 100KB/请求
- 并发请求数 < 5

### 2. 图片加载优化测试

**测试场景**:
- 打卡历史列表 (多张图片)
- 用户头像加载
- 体重秤照片上传

**优化检查点**:
- [ ] 使用图片缓存 (Glide/Coil)
- [ ] 实现懒加载
- [ ] 图片压缩 (质量 80%, 最大宽度 1080px)
- [ ] 使用 WebP 格式
- [ ] 实现占位图和错误图

**性能指标**:
- 图片加载时间 < 1s
- 内存占用 < 50MB (20张图片)
- 缓存命中率 > 80%

### 3. 内存使用测试

**测试工具**: Android Profiler - Memory

**测试步骤**:
1. 启动应用
2. 执行各种操作 (浏览、创建、打卡)
3. 观察内存使用曲线
4. 检查是否有内存泄漏

**优化检查点**:
- [ ] 及时释放不用的资源
- [ ] 避免 Activity/Fragment 泄漏
- [ ] 使用 WeakReference
- [ ] 及时取消网络请求
- [ ] 清理 Bitmap 缓存

**性能指标**:
- 应用内存占用 < 150MB
- 无明显内存泄漏
- GC 频率 < 10次/分钟

### 4. 电池消耗测试

**测试工具**: Battery Historian

**测试步骤**:
```bash
# 1. 重置电池统计
adb shell dumpsys batterystats --reset

# 2. 使用应用 30 分钟

# 3. 导出电池统计
adb bugreport > bugreport.zip

# 4. 上传到 Battery Historian 分析
# https://bathist.ef.lc/
```

**优化检查点**:
- [ ] 避免频繁的网络请求
- [ ] 使用 WorkManager 替代定时任务
- [ ] 合理使用后台服务
- [ ] 优化定位服务使用
- [ ] 减少 CPU 唤醒次数

**性能指标**:
- 30分钟使用电量 < 5%
- 后台电量消耗 < 1%/小时

### 5. 启动时间测试

**测试命令**:
```bash
# 冷启动时间
adb shell am start -W com.weightloss.betting/.ui.MainActivity

# 查看启动时间
# TotalTime: 总启动时间
# WaitTime: 等待时间
```

**优化检查点**:
- [ ] 延迟初始化非必要组件
- [ ] 使用启动画面
- [ ] 优化 Application onCreate
- [ ] 减少主线程工作
- [ ] 使用 Startup Library

**性能指标**:
- 冷启动时间 < 2s
- 热启动时间 < 1s

### 6. UI 渲染性能测试

**测试工具**: GPU Rendering Profiler

**测试步骤**:
1. 开发者选项 > GPU 呈现模式分析 > 在屏幕上显示为条形图
2. 使用应用并观察绿线 (16ms 基准线)
3. 超过绿线表示掉帧

**优化检查点**:
- [ ] 减少布局层级 (< 10层)
- [ ] 使用 ConstraintLayout
- [ ] 避免过度绘制
- [ ] 使用 RecyclerView 替代 ListView
- [ ] 实现 ViewHolder 模式

**性能指标**:
- 帧率 > 55 FPS
- 掉帧率 < 5%
- 布局层级 < 10

### 7. 数据库性能测试

**测试场景**:
- 插入 1000 条打卡记录
- 查询用户的所有计划
- 更新用户信息

**优化检查点**:
- [ ] 使用事务批量插入
- [ ] 添加必要的索引
- [ ] 使用 Room 数据库
- [ ] 异步执行数据库操作
- [ ] 实现分页加载

**性能指标**:
- 单条插入 < 10ms
- 批量插入 (100条) < 100ms
- 查询 < 50ms

## iOS 性能测试

### 1. 网络请求优化测试

**测试工具**: Instruments - Network

**测试步骤**:
1. 打开 Xcode
2. Product > Profile (⌘I)
3. 选择 Network 模板
4. 运行应用并执行操作

**优化检查点**:
- [ ] 使用 URLSession 配置
- [ ] 实现请求缓存
- [ ] 启用 HTTP/2
- [ ] 合并请求
- [ ] 压缩响应

**性能指标**:
- 平均请求时间 < 500ms
- 数据传输量 < 100KB/请求

### 2. 图片加载优化测试

**测试工具**: Instruments - Allocations

**优化检查点**:
- [ ] 使用 SDWebImage/Kingfisher
- [ ] 实现图片缓存
- [ ] 图片压缩和缩放
- [ ] 懒加载
- [ ] 使用 HEIC 格式

**性能指标**:
- 图片加载时间 < 1s
- 内存占用 < 50MB

### 3. 内存使用测试

**测试工具**: Instruments - Leaks & Allocations

**测试步骤**:
1. Product > Profile
2. 选择 Leaks 模板
3. 运行应用并执行各种操作
4. 检查是否有内存泄漏

**优化检查点**:
- [ ] 使用 weak/unowned 避免循环引用
- [ ] 及时释放资源
- [ ] 使用 autoreleasepool
- [ ] 避免大对象常驻内存

**性能指标**:
- 应用内存占用 < 150MB
- 无内存泄漏
- 内存警告次数 = 0

### 4. 电池消耗测试

**测试工具**: Instruments - Energy Log

**测试步骤**:
1. Product > Profile
2. 选择 Energy Log 模板
3. 使用应用 30 分钟
4. 分析能耗报告

**优化检查点**:
- [ ] 减少后台活动
- [ ] 优化定位服务
- [ ] 合理使用推送通知
- [ ] 避免频繁唤醒
- [ ] 使用 Background Tasks

**性能指标**:
- 30分钟使用电量 < 5%
- 后台电量消耗 < 1%/小时

### 5. 启动时间测试

**测试方法**:
```swift
// 在 AppDelegate 中添加
let launchTime = Date()

func application(_ application: UIApplication, 
                didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    let elapsed = Date().timeIntervalSince(launchTime)
    print("Launch time: \(elapsed)s")
    return true
}
```

**优化检查点**:
- [ ] 延迟初始化
- [ ] 减少 didFinishLaunching 工作
- [ ] 使用启动画面
- [ ] 优化依赖注入
- [ ] 异步加载资源

**性能指标**:
- 冷启动时间 < 2s
- 热启动时间 < 1s

### 6. UI 渲染性能测试

**测试工具**: Instruments - Core Animation

**测试步骤**:
1. Product > Profile
2. 选择 Core Animation 模板
3. 启用 "Color Blended Layers"
4. 观察红色区域 (过度混合)

**优化检查点**:
- [ ] 设置 opaque = true
- [ ] 避免透明背景
- [ ] 减少视图层级
- [ ] 使用 CALayer 优化
- [ ] 实现视图复用

**性能指标**:
- 帧率 > 55 FPS
- 掉帧率 < 5%

### 7. Core Data 性能测试

**测试场景**:
- 批量插入数据
- 复杂查询
- 数据迁移

**优化检查点**:
- [ ] 使用批量操作
- [ ] 添加索引
- [ ] 使用 NSFetchedResultsController
- [ ] 异步执行
- [ ] 实现分页

**性能指标**:
- 单条插入 < 10ms
- 批量插入 (100条) < 100ms
- 查询 < 50ms

## 通用优化建议

### 1. 网络优化
- 实现请求缓存策略
- 使用 CDN 加速静态资源
- 启用 HTTP/2
- 实现请求重试和超时
- 合并小请求

### 2. 图片优化
- 使用适当的图片格式 (WebP/HEIC)
- 实现图片压缩
- 使用缩略图
- 实现懒加载
- 使用图片缓存库

### 3. 数据库优化
- 添加必要的索引
- 使用批量操作
- 异步执行
- 实现分页加载
- 定期清理旧数据

### 4. 内存优化
- 及时释放资源
- 避免内存泄漏
- 使用对象池
- 实现图片缓存限制
- 监控内存使用

### 5. 电池优化
- 减少后台活动
- 合理使用定位
- 批量处理网络请求
- 使用推送通知替代轮询
- 优化动画和渲染

## 性能测试报告模板

### 移动端性能测试报告

**测试日期**: YYYY-MM-DD  
**测试设备**: 
- Android: [设备型号, Android 版本]
- iOS: [设备型号, iOS 版本]

**测试结果**:

| 指标 | Android 目标 | Android 实际 | iOS 目标 | iOS 实际 | 状态 |
|------|-------------|-------------|---------|---------|------|
| 启动时间 | < 2s | XXs | < 2s | XXs | ✅/❌ |
| 内存占用 | < 150MB | XXXMB | < 150MB | XXXMB | ✅/❌ |
| 帧率 | > 55 FPS | XX FPS | > 55 FPS | XX FPS | ✅/❌ |
| 网络请求 | < 500ms | XXXms | < 500ms | XXXms | ✅/❌ |
| 电池消耗 | < 5%/30min | XX% | < 5%/30min | XX% | ✅/❌ |

**性能问题**:
1. [描述发现的问题]
2. [描述发现的问题]

**优化建议**:
1. [优化建议]
2. [优化建议]

**结论**:
[总体评估]
