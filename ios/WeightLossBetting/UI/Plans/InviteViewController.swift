import UIKit

class InviteViewController: UIViewController {
    
    // MARK: - Properties
    
    private var planId: String?
    private let repository = BettingPlanRepository.shared
    
    private var searchTextField: UITextField!
    private var searchButton: UIButton!
    private var inviteButton: UIButton!
    private var resultLabel: UILabel!
    private var userInfoLabel: UILabel!
    private var loadingIndicator: UIActivityIndicatorView!
    
    private var searchedUserEmail: String?  // 存储搜索到的用户邮箱
    private var searchedUserId: String? // 存储搜索到的用户 id
    private var onInviteSelected: ((String) -> Void)? // 如果提供，则为创建前邀请流程回调（传入 inviteeId）

    // MARK: - Initialization
    
    init(planId: String) {
        self.planId = planId
        super.init(nibName: nil, bundle: nil)
    }

    /// 初始化用于创建前邀请流程：不需要已有 planId，邀请后会回调 inviteeId
    init(onInviteSelected: @escaping (String) -> Void) {
        self.onInviteSelected = onInviteSelected
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
        
        // Search user label
        let searchLabel = UILabel()
        searchLabel.text = "搜索用户"
        searchLabel.font = .systemFont(ofSize: 16, weight: .medium)
        searchLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(searchLabel)
        
        // Search text field
        searchTextField = UITextField()
        searchTextField.placeholder = "请输入好友的邮箱地址"
        searchTextField.borderStyle = .roundedRect
        searchTextField.autocapitalizationType = .none
        searchTextField.keyboardType = .emailAddress
        searchTextField.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(searchTextField)
        
        // Search button
        searchButton = UIButton(type: .system)
        searchButton.setTitle("搜索", for: .normal)
        searchButton.titleLabel?.font = .boldSystemFont(ofSize: 16)
        searchButton.backgroundColor = .systemGreen
        searchButton.setTitleColor(.white, for: .normal)
        searchButton.layer.cornerRadius = 10
        searchButton.addTarget(self, action: #selector(searchTapped), for: .touchUpInside)
        searchButton.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(searchButton)
        
        // Result label
        resultLabel = UILabel()
        resultLabel.text = ""
        resultLabel.font = .systemFont(ofSize: 14)
        resultLabel.textColor = .systemGreen
        resultLabel.numberOfLines = 0
        resultLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(resultLabel)
        
        // User info label (display found user info)
        userInfoLabel = UILabel()
        userInfoLabel.text = ""
        userInfoLabel.font = .systemFont(ofSize: 14)
        userInfoLabel.textColor = .secondaryLabel
        userInfoLabel.numberOfLines = 0
        userInfoLabel.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(userInfoLabel)
        
        // Invite button (initially hidden)
        inviteButton = UIButton(type: .system)
        inviteButton.setTitle("发送邀请", for: .normal)
        inviteButton.titleLabel?.font = .boldSystemFont(ofSize: 18)
        inviteButton.backgroundColor = .systemBlue
        inviteButton.setTitleColor(.white, for: .normal)
        inviteButton.layer.cornerRadius = 12
        inviteButton.addTarget(self, action: #selector(inviteTapped), for: .touchUpInside)
        inviteButton.translatesAutoresizingMaskIntoConstraints = false
        inviteButton.isHidden = true  // 初始隐藏，搜索到用户后才显示
        view.addSubview(inviteButton)
        
        // Loading indicator
        loadingIndicator = UIActivityIndicatorView(style: .medium)
        loadingIndicator.hidesWhenStopped = true
        loadingIndicator.translatesAutoresizingMaskIntoConstraints = false
        view.addSubview(loadingIndicator)
        
        // Layout
        NSLayoutConstraint.activate([
            searchLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 30),
            searchLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            searchLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            searchTextField.topAnchor.constraint(equalTo: searchLabel.bottomAnchor, constant: 8),
            searchTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            searchTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            searchTextField.heightAnchor.constraint(equalToConstant: 44),
            
            searchButton.topAnchor.constraint(equalTo: searchTextField.bottomAnchor, constant: 12),
            searchButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            searchButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            searchButton.heightAnchor.constraint(equalToConstant: 44),
            
            resultLabel.topAnchor.constraint(equalTo: searchButton.bottomAnchor, constant: 16),
            resultLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            resultLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            userInfoLabel.topAnchor.constraint(equalTo: resultLabel.bottomAnchor, constant: 8),
            userInfoLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            userInfoLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            inviteButton.topAnchor.constraint(equalTo: userInfoLabel.bottomAnchor, constant: 30),
            inviteButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            inviteButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            inviteButton.heightAnchor.constraint(equalToConstant: 50),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: searchButton.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: searchButton.centerYAnchor)
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
    
    @objc private func searchTapped() {
        guard let email = searchTextField.text?.trimmingCharacters(in: .whitespacesAndNewlines),
              !email.isEmpty else {
            showError("请输入邮箱地址")
            return
        }
        
        // Validate email format
        let emailRegex = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$"
        let emailPredicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
        if !emailPredicate.evaluate(with: email) {
            showError("请输入有效的邮箱地址")
            return
        }
        
        searchUser(email: email)
    }
    
    @objc private func inviteTapped() {
        guard let inviteeId = searchedUserId, !inviteeId.isEmpty else {
            showError("请先搜索用户")
            return
        }

        // If onInviteSelected is provided, we're in "create-before-invite" flow
        if let onInvite = onInviteSelected {
            // 先关闭邀请页面，让 CreatePlanVC 去创建计划
            dismiss(animated: true) {
                // 回调传入 inviteeId，触发创建计划
                onInvite(inviteeId)
            }
            return
        }

        // Normal flow: invite for existing plan
        guard let _ = self.planId else {
            showError("计划 ID 无效，无法发送邀请")
            return
        }
        guard let email = searchedUserEmail else {
            showError("无法获取被邀请者邮箱")
            return
        }

        sendInvite(to: email)
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    // MARK: - Private Methods
    
    private func searchUser(email: String) {
        searchButton.isEnabled = false
        loadingIndicator.startAnimating()
        searchButton.setTitle("", for: .normal)
        
        // 清空之前的搜索结果
        resultLabel.text = ""
        userInfoLabel.text = ""
        inviteButton.isHidden = true
        searchedUserEmail = nil
        
        // 调用实际的搜索 API
        UserRepository.shared.searchUserByEmail(email: email) { [weak self] result in
            DispatchQueue.main.async {
                self?.searchButton.isEnabled = true
                self?.loadingIndicator.stopAnimating()
                self?.searchButton.setTitle("搜索", for: .normal)

                switch result {
                case .success(let user):
                    self?.resultLabel.text = "✅ 找到用户"
                    self?.resultLabel.textColor = .systemGreen
                    let nicknameText = user.nickname ?? "(未设置)"
                    self?.userInfoLabel.text = "昵称：\(nicknameText)\n\n请确认这是您要邀请的好友"
                    self?.inviteButton.isHidden = false
                    self?.searchedUserEmail = user.email ?? email
                    self?.searchedUserId = user.id

                case .failure(let error):
                    self?.resultLabel.text = "❌ 未找到用户"
                    self?.resultLabel.textColor = .systemRed
                    self?.userInfoLabel.text = "邮箱：\(email)\n\n该用户不存在或未注册"
                    self?.inviteButton.isHidden = true
                    self?.searchedUserEmail = nil
                }
            }
        }
    }
    
    private func sendInvite(to inviteeEmail: String) {
        inviteButton.isEnabled = false
        loadingIndicator.startAnimating()
        inviteButton.setTitle("", for: .normal)
        
        guard let planId = self.planId else {
            self.inviteButton.isEnabled = true
            self.loadingIndicator.stopAnimating()
            self.inviteButton.setTitle("发送邀请", for: .normal)
            showError("计划 ID 无效，无法发送邀请")
            return
        }

        repository.inviteParticipant(planId: planId, inviteeEmail: inviteeEmail) { [weak self] result in
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
        let alert = UIAlertController(title: "成功", message: "邀请已发送，即将进入计划详情", preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
            // 先关闭邀请页面
            self?.dismiss(animated: true) { [weak self] in
                guard let strongSelf = self else { return }
                
                // 如果是"创建前邀请"流程（planId 为 nil），则不需要导航，由 CreatePlanVC 处理
                if strongSelf.planId == nil {
                    print("✅ [InviteVC] 创建前邀请流程，由 CreatePlanVC 处理导航")
                    return
                }
                
                // 找到创建计划页面并关闭
                // InviteVC 是被 UINavigationController 包装后 present 的
                // 所以 navigationController?.presentingViewController 就是 CreatePlanVC
                if let creatingVC = strongSelf.navigationController?.presentingViewController as? CreatePlanViewController {
                    creatingVC.dismiss(animated: true) { [weak self] in
                        guard let strongSelf = self else { return }
                        // 延迟一点点，确保页面完全关闭
                        DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
                            guard let strongSelf = self else { return }
                            strongSelf.navigateToPlanDetail(planId: strongSelf.planId!)
                        }
                    }
                } else {
                    // 如果创建计划页面已经被关了，直接打开详情
                    DispatchQueue.main.asyncAfter(deadline: .now() + 0.3) { [weak self] in
                        guard let strongSelf = self else { return }
                        strongSelf.navigateToPlanDetail(planId: strongSelf.planId!)
                    }
                }
            }
        })
        present(alert, animated: true)
    }
    
    private func navigateToPlanDetail(planId: String) {
        // 尝试从当前呈现的视图控制器中找到导航控制器
        var targetNavController: UINavigationController?
        
        // 方法 1：如果当前视图控制器还在导航栈中
        if let nav = self.navigationController {
            targetNavController = nav
        }
        
        // 方法 2：通过 SceneDelegate 获取主导航控制器
        if targetNavController == nil,
           let sceneDelegate = UIApplication.shared.connectedScenes.first?.delegate as? SceneDelegate,
           let window = sceneDelegate.window,
           let rootViewController = window.rootViewController {
            if let mainNav = rootViewController as? UINavigationController {
                targetNavController = mainNav
            } else if let tabBarController = rootViewController as? UITabBarController,
                      let selectedNav = tabBarController.selectedViewController as? UINavigationController {
                targetNavController = selectedNav
            }
        }
        
        // 执行导航
        if let navController = targetNavController {
            // 先 pop 到根控制器，避免重复 push
            navController.popToRootViewController(animated: false)
            
            // Push 计划详情页面
            let planDetailVC = PlanDetailViewController(planId: planId)
            navController.pushViewController(planDetailVC, animated: true)
            print("✅ [InviteVC] 已导航到计划详情页面：\(planId)")
        } else {
            print("❌ [InviteVC] 无法找到导航控制器，无法跳转到计划详情")
        }
    }
}
