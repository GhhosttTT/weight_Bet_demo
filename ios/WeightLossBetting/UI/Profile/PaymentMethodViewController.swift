import UIKit
import StripePaymentSheet

final class PaymentMethodViewController: UIViewController {
    private let securityMessage: UILabel = {
        let label = UILabel()
        label.text = "生产环境使用 Stripe 安全组件处理卡信息。应用不会读取或保存完整银行卡号、有效期和安全码。"
        label.font = .systemFont(ofSize: 16)
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let detailMessage: UILabel = {
        let label = UILabel()
        label.text = "充值时会在 Stripe 支付页面中选择银行卡；提现请使用 Stripe Connect 设置提现账户。"
        label.font = .systemFont(ofSize: 14)
        label.textColor = AppTheme.Colors.secondaryLabel
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let setupButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("使用 Stripe 安全设置", for: .normal)
        button.backgroundColor = AppTheme.Colors.primary
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = AppTheme.CornerRadius.medium
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    private let activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .medium)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()

    private let viewModel = PaymentMethodViewModel()
    private var paymentSheet: PaymentSheet?
    private let userId: String

    init(userId: String) {
        self.userId = userId
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    override func viewDidLoad() {
        super.viewDidLoad()
        title = "绑定支付方式"
        view.backgroundColor = AppTheme.Colors.background
        view.addSubview(securityMessage)
        view.addSubview(detailMessage)
        view.addSubview(setupButton)
        view.addSubview(activityIndicator)

        NSLayoutConstraint.activate([
            securityMessage.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 32),
            securityMessage.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 24),
            securityMessage.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -24),
            detailMessage.topAnchor.constraint(equalTo: securityMessage.bottomAnchor, constant: 16),
            detailMessage.leadingAnchor.constraint(equalTo: securityMessage.leadingAnchor),
            detailMessage.trailingAnchor.constraint(equalTo: securityMessage.trailingAnchor),
            setupButton.topAnchor.constraint(equalTo: detailMessage.bottomAnchor, constant: 32),
            setupButton.leadingAnchor.constraint(equalTo: securityMessage.leadingAnchor),
            setupButton.trailingAnchor.constraint(equalTo: securityMessage.trailingAnchor),
            setupButton.heightAnchor.constraint(equalToConstant: 50),
            activityIndicator.centerXAnchor.constraint(equalTo: setupButton.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: setupButton.centerYAnchor)
        ])

        setupButton.addTarget(self, action: #selector(setupButtonTapped), for: .touchUpInside)
        viewModel.onStateChanged = { [weak self] state in
            DispatchQueue.main.async { self?.handle(state) }
        }
    }

    @objc private func setupButtonTapped() {
        viewModel.createSetupIntent()
    }

    private func handle(_ state: PaymentMethodState) {
        switch state {
        case .idle:
            activityIndicator.stopAnimating()
            setupButton.isEnabled = true
        case .loading:
            activityIndicator.startAnimating()
            setupButton.isEnabled = false
        case .setupIntentReady(let clientSecret):
            var configuration = PaymentSheet.Configuration()
            configuration.merchantDisplayName = "BetFit"
            paymentSheet = PaymentSheet(
                setupIntentClientSecret: clientSecret,
                configuration: configuration
            )
            paymentSheet?.present(from: self) { [weak self] result in
                switch result {
                case .completed: self?.viewModel.setupCompleted()
                case .canceled: self?.viewModel.setupCanceled()
                case .failed(let error): self?.viewModel.setupFailed(error.localizedDescription)
                }
            }
        case .success:
            activityIndicator.stopAnimating()
            showAlert(title: "设置完成", message: "支付方式已通过 Stripe 安全设置") { [weak self] in
                self?.navigationController?.popViewController(animated: true)
            }
        case .error(let message):
            activityIndicator.stopAnimating()
            setupButton.isEnabled = true
            showAlert(title: "设置失败", message: message)
        }
    }

    private func showAlert(title: String, message: String, completion: (() -> Void)? = nil) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { _ in completion?() })
        present(alert, animated: true)
    }
}
