# iOS 打卡功能集成指南

## 概述

本指南说明如何将打卡功能集成到 iOS 应用中。

## 文件结构

```
ios/WeightLossBetting/UI/CheckIn/
├── CheckInViewController.swift          # 打卡界面
├── CheckInViewModel.swift               # 打卡 ViewModel
├── CheckInHistoryViewController.swift   # 打卡历史界面
├── CheckInHistoryViewModel.swift        # 打卡历史 ViewModel
├── ProgressViewController.swift         # 进度展示界面
└── ProgressViewModel.swift              # 进度 ViewModel
```

## 使用方法

### 1. 打卡界面

从计划详情或主界面导航到打卡界面:

```swift
// 在 PlanDetailViewController 或其他地方
let checkInVC = CheckInViewController(planId: plan.id)
navigationController?.pushViewController(checkInVC, animated: true)
```

### 2. 打卡历史界面

查看某个计划的打卡历史:

```swift
// 查看所有打卡记录
let historyVC = CheckInHistoryViewController(planId: plan.id)
navigationController?.pushViewController(historyVC, animated: true)

// 查看特定用户的打卡记录
let historyVC = CheckInHistoryViewController(planId: plan.id, userId: user.id)
navigationController?.pushViewController(historyVC, animated: true)
```

### 3. 进度展示界面

查看用户在某个计划中的进度:

```swift
let progressVC = ProgressViewController(planId: plan.id, userId: user.id)
navigationController?.pushViewController(progressVC, animated: true)
```

## 权限配置

### Info.plist 配置

打卡功能需要相机和相册权限,请在 `Info.plist` 中添加以下配置:

```xml
<key>NSCameraUsageDescription</key>
<string>需要访问相机以拍摄体重秤照片</string>

<key>NSPhotoLibraryUsageDescription</key>
<string>需要访问相册以选择体重秤照片</string>

<key>NSPhotoLibraryAddUsageDescription</key>
<string>需要保存照片到相册</string>
```

## 功能特性

### 打卡功能

- ✅ 输入体重数据 (30-300kg)
- ✅ 上传体重秤照片 (可选)
- ✅ 添加备注 (可选)
- ✅ 自动照片压缩
- ✅ 离线打卡支持
- ✅ 重复打卡检测
- ✅ 友好的错误提示

### 打卡历史

- ✅ 显示所有打卡记录
- ✅ 按日期倒序排列
- ✅ 显示审核状态
- ✅ 下拉刷新
- ✅ 空状态提示

### 进度展示

- ✅ 圆形进度条可视化
- ✅ 当前体重显示
- ✅ 初始/目标体重对比
- ✅ 已减重量统计
- ✅ 打卡次数统计
- ✅ 剩余天数统计
- ✅ 下拉刷新

## 数据流

### 打卡流程

```
用户输入体重
    ↓
选择照片 (可选)
    ↓
照片自动压缩上传
    ↓
提交打卡数据
    ↓
CheckInViewModel 验证
    ↓
CheckInRepository 处理
    ↓
在线: APIService → Backend
离线: OfflineSyncManager → 本地队列
    ↓
成功: 返回上一页
失败: 显示错误提示
```

### 离线同步流程

```
离线打卡
    ↓
保存到本地队列 (CoreData)
    ↓
显示临时打卡记录
    ↓
网络恢复
    ↓
OfflineSyncManager 自动同步
    ↓
同步成功: 更新打卡记录
同步失败: 保留在队列中,下次重试
```

## 错误处理

### 常见错误

1. **体重范围错误**
   - 错误: "体重必须在30-300kg之间"
   - 解决: 检查输入的体重数值

2. **重复打卡错误**
   - 错误: "今日已打卡,请明天再来"
   - 解决: 每天只能打卡一次

3. **日期范围错误**
   - 错误: "打卡日期不在计划期间内"
   - 解决: 只能在计划开始和结束日期之间打卡

4. **网络错误**
   - 错误: "网络连接失败"
   - 解决: 检查网络连接,或使用离线打卡功能

5. **照片上传错误**
   - 错误: "照片上传失败"
   - 解决: 检查网络连接,或稍后重试

## 自定义配置

### 修改照片压缩质量

在 `CheckInViewController.swift` 中修改 `compressImage` 方法:

```swift
private func compressImage(_ image: UIImage) -> Data? {
    let maxSize: CGFloat = 1024  // 修改最大尺寸
    var compression: CGFloat = 0.8  // 修改压缩质量 (0.0-1.0)
    
    // ... 其他代码
}
```

### 修改缓存过期时间

在 `CacheManager.swift` 中修改:

```swift
private let checkInCacheExpiration: TimeInterval = 300 // 5 分钟,可以修改
```

## 测试

### 手动测试步骤

1. **打卡功能测试:**
   - 打开打卡界面
   - 输入体重 (测试有效值和无效值)
   - 选择照片 (测试相机和相册)
   - 添加备注
   - 提交打卡
   - 验证成功提示

2. **重复打卡测试:**
   - 同一天内尝试打卡两次
   - 验证错误提示

3. **离线打卡测试:**
   - 关闭网络
   - 进行打卡
   - 验证临时记录显示
   - 打开网络
   - 验证自动同步

4. **打卡历史测试:**
   - 打开打卡历史界面
   - 验证记录显示
   - 测试下拉刷新
   - 验证空状态

5. **进度展示测试:**
   - 打开进度展示界面
   - 验证进度计算
   - 验证统计数据
   - 测试下拉刷新

## 常见问题

### Q: 照片上传失败怎么办?

A: 照片上传失败不会影响打卡提交。打卡数据会正常保存,只是没有照片。用户可以稍后重新上传照片。

### Q: 离线打卡的数据会丢失吗?

A: 不会。离线打卡的数据会保存到本地 CoreData 数据库,网络恢复后会自动同步到服务器。

### Q: 如何查看离线队列中的打卡数据?

A: 可以通过 `CheckInRepository.getPendingSyncCount()` 查看待同步的打卡数量。

### Q: 打卡历史显示的是所有用户的记录吗?

A: 默认显示计划中所有用户的打卡记录。如果只想显示特定用户的记录,可以在初始化时传入 `userId` 参数。

### Q: 进度百分比如何计算?

A: 进度百分比 = (已减重量 / 目标减重量) × 100%。如果进度超过 100%,会显示为 100%。

## 后续开发

### 添加体重变化图表

1. 安装 Charts 库:
   ```ruby
   pod 'Charts'
   ```

2. 在 `ProgressViewController` 中集成图表:
   ```swift
   import Charts
   
   private let lineChartView: LineChartView = {
       let chartView = LineChartView()
       chartView.translatesAutoresizingMaskIntoConstraints = false
       return chartView
   }()
   
   func updateChart(with checkIns: [CheckIn]) {
       var entries: [ChartDataEntry] = []
       
       for (index, checkIn) in checkIns.enumerated() {
           let entry = ChartDataEntry(x: Double(index), y: checkIn.weight)
           entries.append(entry)
       }
       
       let dataSet = LineChartDataSet(entries: entries, label: "体重变化")
       dataSet.colors = [.systemBlue]
       dataSet.circleColors = [.systemBlue]
       dataSet.lineWidth = 2
       
       let data = LineChartData(dataSet: dataSet)
       lineChartView.data = data
   }
   ```

### 添加打卡提醒通知

1. 请求通知权限
2. 创建本地通知
3. 在每天固定时间提醒用户打卡

### 添加打卡日历视图

1. 使用 FSCalendar 或自定义日历视图
2. 在日历上标记已打卡的日期
3. 点击日期查看当天的打卡详情

## 总结

iOS 打卡功能已完整实现,包括:

- ✅ 打卡界面 (体重输入、照片上传、备注)
- ✅ 照片上传功能 (相机、相册、压缩)
- ✅ 打卡历史界面 (列表展示、下拉刷新)
- ✅ 进度展示界面 (圆形进度条、统计卡片)
- ✅ 离线支持 (本地队列、自动同步)
- ✅ 错误处理 (友好提示、重试机制)

所有功能都遵循 MVVM 架构,代码质量良好,可以直接集成到主项目中。
