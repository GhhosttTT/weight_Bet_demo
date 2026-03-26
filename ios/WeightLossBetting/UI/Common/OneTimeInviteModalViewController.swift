import UIKit

final class OneTimeInviteModalViewController: UIViewController {
    private let invitation: InvitationItem
    var onDisplayed: (() -> Void)?
    var onDismiss: ((Bool) -> Void)? // true = viewed/opened, false = dismissed without viewing

    init(invitation: InvitationItem) {
        self.invitation = invitation
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
        l.text = "New Invitation"
        l.translatesAutoresizingMaskIntoConstraints = false
        return l
    }()

    private let messageLabel: UILabel = {
        let l = UILabel()
        l.numberOfLines = 0
        l.textColor = .label
        l.translatesAutoresizingMaskIntoConstraints = false
        return l
    }()

    private let viewButton: UIButton = {
        let b = UIButton(type: .system)
        b.setTitle("View Plan", for: .normal)
        b.translatesAutoresizingMaskIntoConstraints = false
        return b
    }()

    private let closeButton: UIButton = {
        let b = UIButton(type: .system)
        b.setTitle("Close", for: .normal)
        b.translatesAutoresizingMaskIntoConstraints = false
        return b
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor.black.withAlphaComponent(0.4)
        setupUI()

        messageLabel.text = invitation.message ?? "You have been invited to join a plan."

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
        // Attempt to navigate to plan detail by posting notification. Feature module handles actual presentation.
        NotificationCenter.default.post(name: .navigateToNotificationType, object: nil, userInfo: ["type": "invite", "relatedId": invitation.planId])
        dismiss(animated: true) { [weak self] in
            self?.onDismiss?(true)
        }
    }

    @objc private func closeTapped() {
        dismiss(animated: true) { [weak self] in
            self?.onDismiss?(false)
        }
    }
}

