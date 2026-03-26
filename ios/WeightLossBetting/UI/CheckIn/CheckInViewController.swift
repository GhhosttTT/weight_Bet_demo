import UIKit

class CheckInViewController: UIViewController {
    
    // MARK: - Properties
    
    private let viewModel = CheckInViewModel()
    private var planId: String
    private var selectedImage: UIImage?
    
    // Public property to set plan ID from notification navigation
    var selectedPlanId: String? {
        didSet {
            if let selectedPlanId = selectedPlanId {
                self.planId = selectedPlanId
            }
        }
    }
    
    // MARK: - UI Components
    
    private let scrollView: UIScrollView = {
        let scrollView = UIScrollView()
        scrollView.translatesAutoresizingMaskIntoConstraints = false
        return scrollView
    }()
    
    private let contentView: UIView = {
        let view = UIView()
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "记录今日体重"
        label.font = .systemFont(ofSize: 24, weight: .bold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let weightTextField: UITextField = {
        let textField = UITextField()
        textField.placeholder = "当前体重 (kg)"
        textField.keyboardType = .decimalPad
        textField.borderStyle = .roundedRect
        textField.translatesAutoresizingMaskIntoConstraints = false
        return textField
    }()
    
    private let photoLabel: UILabel = {
        let label = UILabel()
        label.text = "上传体重秤照片 (可选)"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let photoImageView: UIImageView = {
        let imageView = UIImageView()
        imageView.contentMode = .scaleAspectFill
        imageView.clipsToBounds = true
        imageView.backgroundColor = .systemGray5
        imageView.layer.cornerRadius = 8
        imageView.translatesAutoresizingMaskIntoConstraints = false
        return imageView
    }()
    
    private let selectPhotoButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("选择照片", for: .normal)
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let photoProgressView: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .medium)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    private let noteTextView: UITextView = {
        let textView = UITextView()
        textView.font = .systemFont(ofSize: 16)
        textView.layer.borderColor = UIColor.systemGray4.cgColor
        textView.layer.borderWidth = 1
        textView.layer.cornerRadius = 8
        textView.translatesAutoresizingMaskIntoConstraints = false
        return textView
    }()
    
    private let notePlaceholderLabel: UILabel = {
        let label = UILabel()
        label.text = "备注 (可选)"
        label.font = .systemFont(ofSize: 16)
        label.textColor = .placeholderText
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let submitButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("提交打卡", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 16, weight: .semibold)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let loadingIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    // MARK: - Initialization
    
    init(planId: String = "") {
        self.planId = planId
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "每日打卡"
        view.backgroundColor = .systemBackground
        
        setupUI()
        setupBindings()
        setupKeyboardHandling()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        
        contentView.addSubview(titleLabel)
        contentView.addSubview(weightTextField)
        contentView.addSubview(photoLabel)
        contentView.addSubview(photoImageView)
        contentView.addSubview(selectPhotoButton)
        contentView.addSubview(photoProgressView)
        contentView.addSubview(noteTextView)
        contentView.addSubview(notePlaceholderLabel)
        contentView.addSubview(submitButton)
        contentView.addSubview(loadingIndicator)
        
        NSLayoutConstraint.activate([
            scrollView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
            scrollView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            scrollView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            scrollView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            contentView.topAnchor.constraint(equalTo: scrollView.topAnchor),
            contentView.leadingAnchor.constraint(equalTo: scrollView.leadingAnchor),
            contentView.trailingAnchor.constraint(equalTo: scrollView.trailingAnchor),
            contentView.bottomAnchor.constraint(equalTo: scrollView.bottomAnchor),
            contentView.widthAnchor.constraint(equalTo: scrollView.widthAnchor),
            
            titleLabel.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            titleLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            titleLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            
            weightTextField.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 24),
            weightTextField.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            weightTextField.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            weightTextField.heightAnchor.constraint(equalToConstant: 44),
            
            photoLabel.topAnchor.constraint(equalTo: weightTextField.bottomAnchor, constant: 24),
            photoLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            photoLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            
            photoImageView.topAnchor.constraint(equalTo: photoLabel.bottomAnchor, constant: 8),
            photoImageView.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            photoImageView.widthAnchor.constraint(equalToConstant: 200),
            photoImageView.heightAnchor.constraint(equalToConstant: 200),
            
            selectPhotoButton.topAnchor.constraint(equalTo: photoImageView.bottomAnchor, constant: 8),
            selectPhotoButton.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            photoProgressView.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            photoProgressView.topAnchor.constraint(equalTo: selectPhotoButton.bottomAnchor, constant: 8),
            
            noteTextView.topAnchor.constraint(equalTo: photoProgressView.bottomAnchor, constant: 16),
            noteTextView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            noteTextView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            noteTextView.heightAnchor.constraint(equalToConstant: 100),
            
            notePlaceholderLabel.topAnchor.constraint(equalTo: noteTextView.topAnchor, constant: 8),
            notePlaceholderLabel.leadingAnchor.constraint(equalTo: noteTextView.leadingAnchor, constant: 5),
            
            submitButton.topAnchor.constraint(equalTo: noteTextView.bottomAnchor, constant: 32),
            submitButton.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 24),
            submitButton.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -24),
            submitButton.heightAnchor.constraint(equalToConstant: 50),
            
            loadingIndicator.topAnchor.constraint(equalTo: submitButton.bottomAnchor, constant: 16),
            loadingIndicator.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            loadingIndicator.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -24)
        ])
        
        selectPhotoButton.addTarget(self, action: #selector(selectPhotoTapped), for: .touchUpInside)
        submitButton.addTarget(self, action: #selector(submitTapped), for: .touchUpInside)
        
        noteTextView.delegate = self
        
        let tapGesture = UITapGestureRecognizer(target: self, action: #selector(dismissKeyboard))
        view.addGestureRecognizer(tapGesture)
    }
    
    private func setupBindings() {
        viewModel.onPhotoUploadStateChanged = { [weak self] state in
            switch state {
            case .idle:
                self?.photoProgressView.stopAnimating()
                
            case .loading:
                self?.photoProgressView.startAnimating()
                
            case .success:
                self?.photoProgressView.stopAnimating()
                self?.showAlert(title: "成功", message: "照片上传成功")
                
            case .error(let message):
                self?.photoProgressView.stopAnimating()
                self?.showAlert(title: "错误", message: message)
            }
        }
        
        viewModel.onCheckInStateChanged = { [weak self] state in
            switch state {
            case .idle:
                self?.loadingIndicator.stopAnimating()
                self?.submitButton.isEnabled = true
                
            case .loading:
                self?.loadingIndicator.startAnimating()
                self?.submitButton.isEnabled = false
                
            case .success:
                self?.loadingIndicator.stopAnimating()
                self?.submitButton.isEnabled = true
                self?.showAlert(title: "成功", message: "打卡成功") {
                    self?.navigationController?.popViewController(animated: true)
                }
                
            case .error(let message):
                self?.loadingIndicator.stopAnimating()
                self?.submitButton.isEnabled = true
                self?.showAlert(title: "错误", message: message)
            }
        }
    }
    
    private func setupKeyboardHandling() {
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(keyboardWillShow),
            name: UIResponder.keyboardWillShowNotification,
            object: nil
        )
        
        NotificationCenter.default.addObserver(
            self,
            selector: #selector(keyboardWillHide),
            name: UIResponder.keyboardWillHideNotification,
            object: nil
        )
    }
    
    // MARK: - Actions
    
    @objc private func selectPhotoTapped() {
        let alert = UIAlertController(title: "选择照片来源", message: nil, preferredStyle: .actionSheet)
        
        alert.addAction(UIAlertAction(title: "拍照", style: .default) { [weak self] _ in
            self?.openCamera()
        })
        
        alert.addAction(UIAlertAction(title: "从相册选择", style: .default) { [weak self] _ in
            self?.openPhotoLibrary()
        })
        
        alert.addAction(UIAlertAction(title: "取消", style: .cancel))
        
        present(alert, animated: true)
    }
    
    @objc private func submitTapped() {
        guard let weightText = weightTextField.text, !weightText.isEmpty else {
            showAlert(title: "错误", message: "请输入体重")
            return
        }
        
        guard let weight = Double(weightText) else {
            showAlert(title: "错误", message: "请输入有效的体重数值")
            return
        }
        
        let note = noteTextView.text.isEmpty ? nil : noteTextView.text
        
        viewModel.createCheckIn(planId: planId, weight: weight, note: note)
    }
    
    @objc private func dismissKeyboard() {
        view.endEditing(true)
    }
    
    @objc private func keyboardWillShow(notification: NSNotification) {
        guard let keyboardFrame = notification.userInfo?[UIResponder.keyboardFrameEndUserInfoKey] as? CGRect else {
            return
        }
        
        let contentInsets = UIEdgeInsets(top: 0, left: 0, bottom: keyboardFrame.height, right: 0)
        scrollView.contentInset = contentInsets
        scrollView.scrollIndicatorInsets = contentInsets
    }
    
    @objc private func keyboardWillHide(notification: NSNotification) {
        scrollView.contentInset = .zero
        scrollView.scrollIndicatorInsets = .zero
    }
    
    // MARK: - Helper Methods
    
    private func showAlert(title: String, message: String, completion: (() -> Void)? = nil) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default) { _ in
            completion?()
        })
        present(alert, animated: true)
    }
}

// MARK: - UITextViewDelegate

extension CheckInViewController: UITextViewDelegate {
    func textViewDidChange(_ textView: UITextView) {
        notePlaceholderLabel.isHidden = !textView.text.isEmpty
    }
}

// MARK: - UIImagePickerControllerDelegate

extension CheckInViewController: UIImagePickerControllerDelegate, UINavigationControllerDelegate {
    private func openCamera() {
        guard UIImagePickerController.isSourceTypeAvailable(.camera) else {
            showAlert(title: "错误", message: "相机不可用")
            return
        }
        
        let picker = UIImagePickerController()
        picker.sourceType = .camera
        picker.delegate = self
        picker.allowsEditing = true
        present(picker, animated: true)
    }
    
    private func openPhotoLibrary() {
        let picker = UIImagePickerController()
        picker.sourceType = .photoLibrary
        picker.delegate = self
        picker.allowsEditing = true
        present(picker, animated: true)
    }
    
    func imagePickerController(_ picker: UIImagePickerController, didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey : Any]) {
        picker.dismiss(animated: true)
        
        guard let image = info[.editedImage] as? UIImage ?? info[.originalImage] as? UIImage else {
            return
        }
        
        selectedImage = image
        photoImageView.image = image
        
        // Compress and upload image
        if let imageData = compressImage(image) {
            viewModel.uploadPhoto(imageData: imageData)
        }
    }
    
    func imagePickerControllerDidCancel(_ picker: UIImagePickerController) {
        picker.dismiss(animated: true)
    }
    
    private func compressImage(_ image: UIImage) -> Data? {
        let maxSize: CGFloat = 1024
        var compression: CGFloat = 0.8
        
        // Resize image
        let size = image.size
        let scale = min(maxSize / size.width, maxSize / size.height)
        
        let newSize = CGSize(width: size.width * scale, height: size.height * scale)
        
        UIGraphicsBeginImageContextWithOptions(newSize, false, 1.0)
        image.draw(in: CGRect(origin: .zero, size: newSize))
        let resizedImage = UIGraphicsGetImageFromCurrentImageContext()
        UIGraphicsEndImageContext()
        
        // Compress to JPEG
        return resizedImage?.jpegData(compressionQuality: compression)
    }
}
