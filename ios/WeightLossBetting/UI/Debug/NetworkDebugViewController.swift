import UIKit

class NetworkDebugViewController: UIViewController {
    
    private let textView: UITextView = {
        let tv = UITextView()
        tv.isEditable = false
        tv.font = UIFont.monospacedSystemFont(ofSize: 12, weight: .regular)
        tv.backgroundColor = .black
        tv.textColor = .green
        tv.translatesAutoresizingMaskIntoConstraints = false
        return tv
    }()
    
    private let runButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("运行诊断", for: .normal)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()
    
    private let baseURLTextField: UITextField = {
        let tf = UITextField()
        tf.placeholder = "服务器地址"
        tf.text = "http://192.168.1.10:8000/api"
        tf.borderStyle = .roundedRect
        tf.translatesAutoresizingMaskIntoConstraints = false
        return tf
    }()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        title = "网络诊断"
        view.backgroundColor = .systemBackground
        
        setupUI()
        
        runButton.addTarget(self, action: #selector(runDiagnostics), for: .touchUpInside)
        
        // 添加关闭按钮
        navigationItem.rightBarButtonItem = UIBarButtonItem(
            barButtonSystemItem: .close,
            target: self,
            action: #selector(closeTapped)
        )
    }
    
    private func setupUI() {
        view.addSubview(baseURLTextField)
        view.addSubview(runButton)
        view.addSubview(textView)
        
        NSLayoutConstraint.activate([
            baseURLTextField.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            baseURLTextField.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            baseURLTextField.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            baseURLTextField.heightAnchor.constraint(equalToConstant: 44),
            
            runButton.topAnchor.constraint(equalTo: baseURLTextField.bottomAnchor, constant: 16),
            runButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            runButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            runButton.heightAnchor.constraint(equalToConstant: 44),
            
            textView.topAnchor.constraint(equalTo: runButton.bottomAnchor, constant: 16),
            textView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            textView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            textView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor, constant: -16)
        ])
    }
    
    @objc private func runDiagnostics() {
        guard let baseURL = baseURLTextField.text, !baseURL.isEmpty else {
            textView.text = "❌ 请输入服务器地址"
            return
        }
        
        textView.text = "🔄 正在运行诊断...\n"
        runButton.isEnabled = false
        
        NetworkDiagnostics.shared.runFullDiagnostics(baseURL: baseURL) { [weak self] report in
            DispatchQueue.main.async {
                self?.textView.text = report
                self?.runButton.isEnabled = true
            }
        }
    }
    
    @objc private func closeTapped() {
        dismiss(animated: true)
    }
}
