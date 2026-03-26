import UIKit

class InviteViewController: UIViewController {
    
    // MARK: - Properties
    
    private let planId: String
    private let repository = BettingPlanRepository.shared
    
    private var inviteeIdTextField: UITextField!
    private var inviteButton: UIButton!
    private var loadingIndicator: UIActivityIndicatorView!
    
    // MARK: - Initialization
    
    init(planId: String) {
        self.planId = planId
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "邀请参与者"
        view.backgroundColor = .systemBackground
        
        setupUI()
        setupKeyboardHandling()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        // Navigation bar
        navigationItem.leftBarButtonItem = UIBarButtonItem(barButtonSystemItem: .cancel, target: self, action: #selector(cancelTapped))
        
        // Invitee ID label
        let inviteeIdLabel = UILabel()
        inviteeIdLabel.text = "参与者 ID"
        inviteeIdLabel.font = .systemFont(ofSize: 16, weight: .medium)
        inviteeIdLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(inviteeIdLabel)
        
        // Invitee ID text field
        inviteeIdTextField = UITextField()
        inviteeIdTextField.placeholder = "请输入参与者的用户 ID"
        inviteeIdTextField.borderStyle = .roundedRect
        inviteeIdTextField.autocapitalizationType = .none
        inviteeIdTextField.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(inviteeIdTextField)
        
        // Hint label
        let hintLabel = UILabel()
        hintLabel.text = "提示: 您可以在用户个人资料页面找到用户 ID"
        hintLabel.font = .systemFont(ofSize: 14)
        hintLabel.textColor = .secondaryLabel
        hintLabel.numberOfLines = 0
        hintLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(hintLabel)
        
        // Invite button
        inviteButton = UIButton(type: .system)
        inviteButton.setTitle("发送邀请", for: .normal)
        inviteButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        inviteButton.backgroundColor = .systemBlue
        inviteButton.setTitleColor(.white, for: .normal)
        inviteButton.layer.cornerRadius = 12
        inviteButton.addTarget(self, action: #selector(inviteTapped), for: .touchUpInside)
        inviteButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(inviteButton)
        
        // Loading indicator
        loadingIndicator = UIActivityIndicatorView(style: .medium)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(loadingIndicator)
        
        // Layout
        NSLayoutConstraint.activate([
            inviteeIdLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 30),
            inviteeIdLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            inviteeIdLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            inviteeIdTextField.topAnchor.constraint(equalTo: inviteeIdLabel.bottomAnchor, constant: 8),
            inviteeIdTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            inviteeIdTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            inviteeIdTextField.heightAnchor.constraint(equalToConstant: 44),
            
            hintLabel.topAnchor.constraint(equalTo: inviteeIdTextField.bottomAnchor, constant: 8),
            hintLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            hintLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            inviteButton.topAnchor.constraint(equalTo: hintLabel.bottomAnchor, constant: 30),
            inviteButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            inviteButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            inviteButton.heightAnchor.constraint(equalToConstant: 50),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: inviteButton.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: inviteButton.centerYAnchor)
        ])
    }
    
    private func setupKeyboardHandling() {
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
    }
    
    // MARK: - Actions
    
    @objc private func cancelTapped() {
        dismiss(animated: true)
    }
    
    @objc private func inviteTapped() {
        guard let inviteeId = inviteeIdTextField.text?.trimmingCharacters(in: .whitespacesAndNewlines),
              !inviteeId.isEmpty else {
            showError("请输入参与者 ID")
            return
        }
        
        sendInvite(to: inviteeId)
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    // MARK: - Private Methods
    
    private func sendInvite(to inviteeId: String) {
        inviteButton.isEnabled = false
        loadingIndicator.startAnimating()
        inviteButton.setTitle("", for: .normal)
        
        repository.inviteParticipant(planId: planId, inviteeId: inviteeId) { [weak self] result in
            DispatchQueue.main.async {
                self?.inviteButton.isEnabled = true
                self?.loadingIndicator.stopAnimating()
                self?.inviteButton.setTitle("发送邀请", for: .normal)
                
                switch result {
                case .success:
                    self?.showSuccessAndDismiss()
                    
                case .failure(let error):
                    self?.showError(error.localizedDescription)
                }
            }
        }
    }
    
    // MARK: - UI Feedback
    
    private func showError(_ message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
    
    private func showSuccessAndDismiss() {
        let alert = UIAlertController(title: "成功", message: "邀请已发送", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            self?.dismiss(animated: true)
        })
        present(alert, animated: true)
    }
}
