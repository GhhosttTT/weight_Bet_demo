# iOS 支付功能集成指南

## 概述

本指南说明如何将支付功能集成到主应用中。

## 集成步骤

### 1. 从个人资料页面导航到余额页面

在 `ProfileViewController.swift` 中添加余额入口:

```swift
// Add a balance button in ProfileViewController
private let balanceButton: UIButton = {
    let button = UIButton(type: .system)
    button.setTitle("我的余额", for: .normal)
    button.addTarget(self, action: #selector(balanceButtonTapped), for: .touchUpInside)
    return button
}()

@objc private func balanceButtonTapped() {
    let balanceVC = BalanceViewController()
    navigationController?.pushViewController(balanceVC, animated: true)
}
```

### 2. 从计划创建页面检查余额

在 `CreatePlanViewController.swift` 中添加余额检查:

```swift
private func validateBalance(betAmount: Double) {
    let paymentRepository = PaymentRepository()
    
    Task {
        let result = await paymentRepository.getBalance(userId: currentUserId)
        
        switch result {
        case .success(let balance):
            if balance.availableBalance < betAmount {
                showInsufficientBalanceAlert(required: betAmount, available: balance.availableBalance)
            } else {
                // Proceed with plan creation
                createPlan()
            }
        case .failure(let error):
            showAlert(title: "错误", message: "无法获取余额信息")
        }
    }
}

private func showInsufficientBalanceAlert(required: Double, available: Double) {
    let alert = UIAlertController(
        title: "余额不足",
        message: "需要 ¥\(String(format: "%.2f", required)),当前可用余额 ¥\(String(format: "%.2f", available))",
        preferredStyle: .alert
    )
    
    alert.addAction(UIAlertAction(title: "取消", style: .cancel))
    alert.addAction(UIAlertAction(title: "去充值", style: .default) { [weak self] _ in
        let chargeVC = ChargeViewController()
        self?.navigationController?.pushViewController(chargeVC, animated: true)
    })
    
    present(alert, animated: true)
}
```

### 3. 获取当前用户 ID

创建一个 TokenManager 扩展来获取当前用户 ID:

```swift
// In TokenManager.swift or create UserSession.swift
extension TokenManager {
    func getCurrentUserId() -> String? {
        // TODO: Parse JWT token to get user ID
        // For now, return stored user ID
        return UserDefaults.standard.string(forKey: "current_user_id")
    }
    
    func setCurrentUserId(_ userId: String) {
        UserDefaults.standard.set(userId, forKey: "current_user_id")
    }
}
```

然后在所有支付相关的 ViewController 中使用:

```swift
// Replace hardcoded userId with:
let userId = TokenManager.shared.getCurrentUserId() ?? ""
```

### 4. 在登录成功后保存用户 ID

在 `LoginViewController.swift` 中:

```swift
private func handleLoginSuccess(_ authResponse: AuthResponse) {
    // Save tokens
    TokenManager.shared.saveTokens(
        accessToken: authResponse.accessToken,
        refreshToken: authResponse.refreshToken
    )
    
    // Save user ID
    TokenManager.shared.setCurrentUserId(authResponse.user.id)
    
    // Navigate to main screen
    navigateToMainScreen()
}
```

### 5. 添加支付功能到主导航

在 `MainTabBarController` 或主导航中添加支付入口:

```swift
// Option 1: Add to tab bar
let balanceVC = BalanceViewController()
let balanceNav = UINavigationController(rootViewController: balanceVC)
balanceNav.tabBarItem = UITabBarItem(
    title: "余额",
    image: UIImage(systemName: "creditcard"),
    tag: 3
)

// Option 2: Add to profile menu
// See step 1 above
```

## Stripe SDK 集成

### 安装

在 `Podfile` 中添加:

```ruby
pod 'Stripe', '~> 23.0'
```

运行:
```bash
cd ios
pod install
```

### 初始化

在 `AppDelegate.swift` 中:

```swift
import Stripe

func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
    // Initialize Stripe
    StripeAPI.defaultPublishableKey = "pk_test_YOUR_KEY_HERE"
    
    return true
}
```

### 创建支付方法

创建 `StripePaymentHelper.swift`:

```swift
import Stripe

class StripePaymentHelper {
    static let shared = StripePaymentHelper()
    
    private init() {}
    
    func createPaymentMethod(
        cardNumber: String,
        expMonth: Int,
        expYear: Int,
        cvc: String,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        let cardParams = STPCardParams()
        cardParams.number = cardNumber
        cardParams.expMonth = UInt(expMonth)
        cardParams.expYear = UInt(expYear)
        cardParams.cvc = cvc
        
        let paymentMethodParams = STPPaymentMethodParams(
            card: cardParams,
            billingDetails: nil,
            metadata: nil
        )
        
        STPAPIClient.shared.createPaymentMethod(with: paymentMethodParams) { paymentMethod, error in
            if let error = error {
                completion(.failure(error))
            } else if let paymentMethod = paymentMethod {
                completion(.success(paymentMethod.stripeId))
            }
        }
    }
    
    func presentCardForm(
        from viewController: UIViewController,
        completion: @escaping (Result<String, Error>) -> Void
    ) {
        let cardViewController = STPAddCardViewController()
        cardViewController.delegate = self
        
        let navigationController = UINavigationController(rootViewController: cardViewController)
        viewController.present(navigationController, animated: true)
        
        // Store completion handler
        self.cardFormCompletion = completion
    }
    
    private var cardFormCompletion: ((Result<String, Error>) -> Void)?
}

extension StripePaymentHelper: STPAddCardViewControllerDelegate {
    func addCardViewControllerDidCancel(_ addCardViewController: STPAddCardViewController) {
        addCardViewController.dismiss(animated: true)
        cardFormCompletion?(.failure(NSError(domain: "Stripe", code: -1, userInfo: [NSLocalizedDescriptionKey: "User cancelled"])))
    }
    
    func addCardViewController(_ addCardViewController: STPAddCardViewController, didCreatePaymentMethod paymentMethod: STPPaymentMethod, completion: @escaping STPErrorBlock) {
        addCardViewController.dismiss(animated: true)
        cardFormCompletion?(.success(paymentMethod.stripeId))
        completion(nil)
    }
}
```

### 更新充值界面

在 `ChargeViewController.swift` 中:

```swift
@objc private func chargeButtonTapped() {
    guard let amountText = amountTextField.text, !amountText.isEmpty else {
        showAlert(title: "错误", message: "请输入充值金额")
        return
    }
    
    guard let amount = Double(amountText), amount > 0 else {
        showAlert(title: "错误", message: "请输入有效的充值金额")
        return
    }
    
    // Present Stripe card form
    StripePaymentHelper.shared.presentCardForm(from: self) { [weak self] result in
        switch result {
        case .success(let paymentMethodId):
            self?.viewModel.charge(amount: amount, paymentMethodId: paymentMethodId)
        case .failure(let error):
            self?.showAlert(title: "错误", message: error.localizedDescription)
        }
    }
}
```

## 测试

### 测试用例

1. **充值流程:**
   - 打开充值界面
   - 输入金额或选择快捷金额
   - 点击确认充值
   - 验证支付成功/失败提示

2. **余额查询:**
   - 打开余额界面
   - 验证余额显示正确
   - 验证交易历史显示
   - 测试下拉刷新

3. **提现流程:**
   - 打开提现界面
   - 输入提现金额
   - 验证余额不足提示
   - 验证提现成功提示

### Stripe 测试卡号

```
成功: 4242 4242 4242 4242
需要验证: 4000 0025 0000 3155
余额不足: 4000 0000 0000 9995
失败: 4000 0000 0000 0002
```

## 注意事项

1. **安全性:**
   - 不要在客户端存储敏感支付信息
   - 使用 HTTPS 加密通信
   - 验证所有用户输入

2. **用户体验:**
   - 提供清晰的错误提示
   - 显示加载状态
   - 支持下拉刷新

3. **错误处理:**
   - 网络错误重试
   - 支付失败提示
   - 余额不足引导充值

4. **性能:**
   - 使用缓存减少网络请求
   - 优化列表滚动性能
   - 异步加载数据

## 常见问题

### Q: 如何处理支付失败?

A: 在 ViewModel 中捕获错误并显示友好提示:

```swift
case .failure(let error):
    let errorMessage = parseError(error)
    chargeState = .error(errorMessage)
```

### Q: 如何实现支付方式管理?

A: 创建 `PaymentMethodViewController` 来管理用户保存的支付方式:

```swift
class PaymentMethodViewController: UIViewController {
    // List saved payment methods
    // Add new payment method
    // Delete payment method
    // Set default payment method
}
```

### Q: 如何处理充值回调?

A: 后端应该发送推送通知或使用 WebSocket 实时通知客户端:

```swift
// In AppDelegate or NotificationManager
func handlePaymentNotification(_ notification: PaymentNotification) {
    if notification.status == "success" {
        // Refresh balance
        // Show success message
    }
}
```

## 总结

按照以上步骤集成支付功能后,用户可以:

1. 从个人资料页面访问余额页面
2. 查看可用余额和冻结余额
3. 查看交易历史
4. 充值账户
5. 提现收益
6. 在创建计划时自动检查余额

所有功能都已实现并可以直接使用,只需要集成实际的 Stripe SDK 和配置正确的 API 密钥即可。
