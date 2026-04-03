import UIKit

final class DoubleCheckModalViewController: UIViewController {
    let item: DoubleCheckItem
    var onDisplayed: (() -> Void)?
    var onDismiss: ((Bool) -> Void)? // true = viewed/opened, false = dismissed without viewing

    init(item: DoubleCheckItem) {
        self.item = item
        super.init(nibName: nil, bundle: nil)
        modalPresentationStyle = .overFullScreen
        modalTransitionStyle = .crossDissolve
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    private let container: UIView = {
        let v = UIView()
        v.backgroundColor = .systemBackground
        v.layer.cornerRadius = 12
        v.translatesAutoresizingMaskIntoConstraints = false
        return v
    }()

    private let titleLabel: UILabel = {
        let l = UILabel()
        l.font = .boldSystemFont(ofSize: 18)
        l.text = "您有一个计划待二次确认"
        l.translatesAutoresizingMaskIntoConstraints = false
        return l
    }()

    private let messageLabel: UILabel = {
        let l = UILabel()
        l.numberOfLines = 0
        l.textColor = .label
        l.text = "对方已接受计划并提交了目标体重，请您确认后开始计划。"
        l.translatesAutoresizingMaskIntoConstraints = false
        return l
    }()

    private let viewButton: UIButton = {
        let b = UIButton(type: .system)
        b.setTitle("立即查看", for: .normal)
        b.translatesAutoresizingMaskIntoConstraints = false
        return b
    }()

    private let closeButton: UIButton = {
        let b = UIButton(type: .system)
        b.setTitle("稍后再看", for: .normal)
        b.translatesAutoresizingMaskIntoConstraints = false
        return b
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor.black.withAlphaComponent(0.4)
        setupUI()

        viewButton.addTarget(self, action: #selector(viewTapped), for: .touchUpInside)
        closeButton.addTarget(self, action: #selector(closeTapped), for: .touchUpInside)
    }
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
        onDisplayed?()
    }

    private func setupUI() {
        view.addSubview(container)
        container.addSubview(titleLabel)
        container.addSubview(messageLabel)
        container.addSubview(viewButton)
        container.addSubview(closeButton)

        NSLayoutConstraint.activate([
            container.centerYAnchor.constraint(equalTo: view.centerYAnchor),
            container.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 24),
            container.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -24),

            titleLabel.topAnchor.constraint(equalTo: container.topAnchor, constant: 16),
            titleLabel.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 16),
            titleLabel.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -16),

            messageLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            messageLabel.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 16),
            messageLabel.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -16),

            viewButton.topAnchor.constraint(equalTo: messageLabel.bottomAnchor, constant: 16),
            viewButton.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 16),

            closeButton.topAnchor.constraint(equalTo: messageLabel.bottomAnchor, constant: 16),
            closeButton.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -16),

            closeButton.bottomAnchor.constraint(equalTo: container.bottomAnchor, constant: -16)
        ])
    }

    @objc private func viewTapped() {
        let planId = item.planId
        // 先发送通知，避免弹窗释放后无法发送
        print("📢 [DoubleCheckModal] 准备发送导航通知...")
        print("   - 类型：double_check, planId: \(planId)")
        
        NotificationCenter.default.post(
            name: NSNotification.Name(rawValue: "navigateToNotificationType"),
            object: nil,
            userInfo: ["type": "double_check", "relatedId": planId]
        )
        print("✅ [DoubleCheckModal] 通知已发送")
        
        // 再关闭弹窗
        dismiss(animated: true) { [weak self] in
            print("✅ [DoubleCheckModal] 弹窗已关闭")
            self?.onDismiss?(true)
        }
    }

    @objc private func closeTapped() {
        dismiss(animated: true) { [weak self] in
            self?.onDismiss?(false)
        }
    }
}

