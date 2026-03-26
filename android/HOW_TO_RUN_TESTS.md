# 如何运行 Android 测试

## 前置条件

### 1. 安装 Gradle

如果还没有安装 Gradle,可以通过以下方式安装:

#### 方式 1: 使用 Chocolatey (推荐)
```powershell
choco install gradle
```

#### 方式 2: 手动安装
1. 下载 Gradle: https://gradle.org/releases/
2. 解压到目录,例如 `C:\Gradle\gradle-8.2`
3. 添加到 PATH 环境变量:
   - 系统变量 PATH 添加: `C:\Gradle\gradle-8.2\bin`
4. 重启 PowerShell 验证:
   ```powershell
   gradle --version
   ```

#### 方式 3: 使用 Gradle Wrapper (推荐)
在项目根目录运行:
```powershell
# 如果已有 gradle 命令
gradle wrapper --gradle-version 8.2

# 之后可以使用
./gradlew test
```

### 2. 验证 Java 安装

确保 Java 已安装并配置:
```powershell
java -version
```

应该显示 Java 11 或更高版本。

## 运行测试

### 方式 1: 运行所有测试

```powershell
# 进入 android 目录
cd android

# 运行所有测试
gradle test

# 或使用 wrapper
./gradlew test
```

### 方式 2: 运行特定测试类

```powershell
# 运行 Tasks21To24Test
gradle test --tests Tasks21To24Test

# 运行 Tasks18To20Test
gradle test --tests Tasks18To20Test
```

### 方式 3: 运行特定测试方法

```powershell
# 运行单个测试方法
gradle test --tests Tasks21To24Test.test_task21_1_load_user_profile_success
```

### 方式 4: 在 Android Studio 中运行

1. 打开 Android Studio
2. 打开项目: `File > Open > 选择 android 目录`
3. 等待 Gradle 同步完成
4. 右键点击测试文件 `Tasks21To24Test.kt`
5. 选择 `Run 'Tasks21To24Test'`

## 查看测试报告

测试完成后,报告位于:
```
android/app/build/reports/tests/test/index.html
```

在浏览器中打开此文件查看详细的测试报告。

## 测试文件位置

### 任务 21-24 测试
- 文件: `android/app/src/test/java/com/weightloss/betting/Tasks21To24Test.kt`
- 测试用例: 20个
- 覆盖范围:
  - Task 21: 用户信息管理 (3个测试)
  - Task 22: 对赌计划功能 (4个测试)
  - Task 23: 打卡功能 (3个测试)
  - Task 24: 支付功能 (4个测试)
  - 文件和配置 (6个测试)

### 任务 18-20 测试
- 文件: `android/app/src/test/java/com/weightloss/betting/Tasks18To20Test.kt`
- 测试用例: 30+个
- 覆盖范围:
  - Task 18: 网络层
  - Task 19: 本地存储
  - Task 20: 认证功能

## 预期测试结果

### Tasks21To24Test
```
✓ test_task21_1_load_user_profile_success
✓ test_task21_2_update_user_profile_validation
✓ test_task21_3_update_user_profile_success
✓ test_task22_1_load_plan_list_success
✓ test_task22_2_create_plan_validation
✓ test_task22_3_load_plan_detail_success
✓ test_task22_4_accept_plan_success
✓ test_task23_1_create_checkin_validation
✓ test_task23_2_create_checkin_success
✓ test_task23_3_photo_upload_helper_exists
✓ test_task24_1_load_balance_success
✓ test_task24_2_charge_validation
✓ test_task24_3_withdraw_validation
✓ test_task24_4_load_transactions_success
✓ test_layout_files_exist
✓ test_viewmodel_files_exist
✓ test_activity_files_exist
✓ test_manifest_activities_registered
✓ test_permissions_declared
✓ test_comprehensive_user_flow

Total: 20 tests
Expected: 20 passed, 0 failed
Success Rate: 100%
```

## 常见问题

### Q1: 测试失败 - "Cannot resolve symbol"
**原因**: 依赖未正确同步
**解决**:
```powershell
gradle clean build
```

### Q2: 测试失败 - "File not found"
**原因**: 文件路径问题
**解决**: 确保在 `android` 目录下运行测试

### Q3: Gradle 同步失败
**原因**: 网络问题或依赖下载失败
**解决**:
1. 检查网络连接
2. 配置 Gradle 镜像 (如阿里云镜像)
3. 在 `build.gradle` 中添加:
```gradle
repositories {
    maven { url 'https://maven.aliyun.com/repository/public/' }
    maven { url 'https://maven.aliyun.com/repository/google/' }
    google()
    mavenCentral()
}
```

### Q4: 内存不足错误
**解决**: 在 `gradle.properties` 中增加内存:
```properties
org.gradle.jvmargs=-Xmx2048m -XX:MaxPermSize=512m
```

## 调试测试

### 启用详细日志
```powershell
gradle test --info
```

### 查看失败的测试
```powershell
gradle test --tests Tasks21To24Test --info | Select-String "FAILED"
```

### 重新运行失败的测试
```powershell
gradle test --rerun-tasks --tests Tasks21To24Test
```

## 持续集成 (CI)

如果要在 CI 环境中运行测试:

```yaml
# GitHub Actions 示例
- name: Run Tests
  run: |
    cd android
    ./gradlew test --no-daemon
    
- name: Upload Test Report
  uses: actions/upload-artifact@v2
  with:
    name: test-report
    path: android/app/build/reports/tests/
```

## 测试覆盖率

### 生成覆盖率报告
```powershell
gradle test jacocoTestReport
```

### 查看覆盖率报告
报告位于: `android/app/build/reports/jacoco/test/html/index.html`

## 性能测试

### 测试执行时间
```powershell
gradle test --profile
```

报告位于: `android/build/reports/profile/`

## 下一步

测试通过后,可以继续:
1. 运行集成测试
2. 进行 UI 测试 (Espresso)
3. 进行性能测试
4. 准备发布版本

## 相关文档

- [测试结果报告](./TASKS_21-24_TEST_RESULTS.md)
- [Bug 修复总结](./BUG_FIXES_TASKS_21-24.md)
- [实现总结](./TASKS_21-24_IMPLEMENTATION_SUMMARY.md)
- [实现指南](./TASKS_21-24_IMPLEMENTATION.md)

## 联系支持

如果遇到问题:
1. 查看测试报告中的错误信息
2. 检查 `build/` 目录下的日志文件
3. 参考相关文档
4. 提交 Issue 或联系开发团队

---

**文档版本**: 1.0
**最后更新**: 2024年
**维护者**: Kiro AI Assistant
