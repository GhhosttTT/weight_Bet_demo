import UIKit

final class DoubleCheckModalViewController: UIViewController {
    let item: DoubleCheckItem
    var onAction: ((_ action: String, _ comment: String?) -> Void)?

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
        l.text = "Confirm Participant Submission"
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

    private let confirmButton: UIButton = {
        let b = UIButton(type: .system)
        b.setTitle("Confirm", for: .normal)
        b.translatesAutoresizingMaskIntoConstraints = false
        return b
    }()

    private let cancelButton: UIButton = {
        let b = UIButton(type: .system)
        b.setTitle("Cancel Plan", for: .normal)
        b.translatesAutoresizingMaskIntoConstraints = false
        return b
    }()

    private let commentField: UITextField = {
        let f = UITextField()
        f.placeholder = "Optional comment"
        f.borderStyle = .roundedRect
        f.translatesAutoresizingMaskIntoConstraints = false
        return f
    }()

    override func viewDidLoad() {
        super.viewDidLoad()
        view.backgroundColor = UIColor.black.withAlphaComponent(0.4)
        setupUI()

        messageLabel.text = "Participant has submitted their target. Please confirm or cancel the plan."

        confirmButton.addTarget(self, action: #selector(confirmTapped), for: .touchUpInside)
        cancelButton.addTarget(self, action: #selector(cancelTapped), for: .touchUpInside)
    }

    private func setupUI() {
        view.addSubview(container)
        container.addSubview(titleLabel)
        container.addSubview(messageLabel)
        container.addSubview(commentField)
        container.addSubview(confirmButton)
        container.addSubview(cancelButton)

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

            commentField.topAnchor.constraint(equalTo: messageLabel.bottomAnchor, constant: 12),
            commentField.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 16),
            commentField.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -16),
            commentField.heightAnchor.constraint(equalToConstant: 40),

            confirmButton.topAnchor.constraint(equalTo: commentField.bottomAnchor, constant: 12),
            confirmButton.leadingAnchor.constraint(equalTo: container.leadingAnchor, constant: 16),

            cancelButton.topAnchor.constraint(equalTo: commentField.bottomAnchor, constant: 12),
            cancelButton.trailingAnchor.constraint(equalTo: container.trailingAnchor, constant: -16),

            cancelButton.bottomAnchor.constraint(equalTo: container.bottomAnchor, constant: -16)
        ])
    }

    @objc private func confirmTapped() {
        let comment = commentField.text?.isEmpty == true ? nil : commentField.text
        dismiss(animated: true) { [weak self] in
            self?.onAction?("confirm", comment)
        }
    }

    @objc private func cancelTapped() {
        let comment = commentField.text?.isEmpty == true ? nil : commentField.text
        dismiss(animated: true) { [weak self] in
            self?.onAction?("cancel", comment)
        }
    }
}

