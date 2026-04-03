import UIKit

class ProgressViewController: UIViewController {
    
    // MARK: - Properties
    
    private let viewModel = ProgressViewModel()
    private var planId: String
    private var userId: String
    
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
    
    private let progressCircleView: ProgressCircleView = {
        let view = ProgressCircleView()
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let currentWeightLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 16)
        label.textColor = .secondaryLabel
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let currentWeightValueLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 32, weight: .bold)
        label.textColor = .label
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let statsStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let initialWeightCard = StatCard(title: "初始体重")
    private let targetWeightCard = StatCard(title: "目标体重")
    private let weightLossCard = StatCard(title: "已减重")
    
    private let checkInStatsStackView: UIStackView = {
        let stackView = UIStackView()
        stackView.axis = .horizontal
        stackView.distribution = .fillEqually
        stackView.spacing = 16
        stackView.translatesAutoresizingMaskIntoConstraints = false
        return stackView
    }()
    
    private let checkInCountCard = StatCard(title: "打卡次数")
    private let daysRemainingCard = StatCard(title: "剩余天数")
    
    private let chartContainerView: UIView = {
        let view = UIView()
        view.backgroundColor = .systemBackground
        view.layer.cornerRadius = 12
        view.layer.shadowColor = UIColor.black.cgColor
        view.layer.shadowOpacity = 0.1
        view.layer.shadowOffset = CGSize(width: 0, height: 2)
        view.layer.shadowRadius = 4
        view.translatesAutoresizingMaskIntoConstraints = false
        return view
    }()
    
    private let chartTitleLabel: UILabel = {
        let label = UILabel()
        label.text = "体重变化趋势"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let chartPlaceholderLabel: UILabel = {
        let label = UILabel()
        label.text = "暂无数据"
        label.textAlignment = .center
        label.textColor = .secondaryLabel
        label.font = .systemFont(ofSize: 14)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let loadingIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.hidesWhenStopped = true
        indicator.translatesAutoresizingMaskIntoConstraints = false
        return indicator
    }()
    
    private let refreshControl = UIRefreshControl()
    
    // MARK: - Initialization
    
    init(planId: String, userId: String) {
        self.planId = planId
        self.userId = userId
        super.init(nibName: nil, bundle: nil)
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = "进度统计"
        view.backgroundColor = .systemGroupedBackground
        
        setupUI()
        setupBindings()
        loadProgress()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        view.addSubview(scrollView)
        scrollView.addSubview(contentView)
        view.addSubview(loadingIndicator)
        
        contentView.addSubview(progressCircleView)
        contentView.addSubview(currentWeightLabel)
        contentView.addSubview(currentWeightValueLabel)
        contentView.addSubview(statsStackView)
        contentView.addSubview(checkInStatsStackView)
        contentView.addSubview(chartContainerView)
        
        chartContainerView.addSubview(chartTitleLabel)
        chartContainerView.addSubview(chartPlaceholderLabel)
        
        statsStackView.addArrangedSubview(initialWeightCard)
        statsStackView.addArrangedSubview(targetWeightCard)
        statsStackView.addArrangedSubview(weightLossCard)
        
        checkInStatsStackView.addArrangedSubview(checkInCountCard)
        checkInStatsStackView.addArrangedSubview(daysRemainingCard)
        
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
            
            progressCircleView.topAnchor.constraint(equalTo: contentView.topAnchor, constant: 24),
            progressCircleView.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            progressCircleView.widthAnchor.constraint(equalToConstant: 200),
            progressCircleView.heightAnchor.constraint(equalToConstant: 200),
            
            currentWeightLabel.topAnchor.constraint(equalTo: progressCircleView.bottomAnchor, constant: 16),
            currentWeightLabel.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            currentWeightValueLabel.topAnchor.constraint(equalTo: currentWeightLabel.bottomAnchor, constant: 4),
            currentWeightValueLabel.centerXAnchor.constraint(equalTo: contentView.centerXAnchor),
            
            statsStackView.topAnchor.constraint(equalTo: currentWeightValueLabel.bottomAnchor, constant: 32),
            statsStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            statsStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            statsStackView.heightAnchor.constraint(equalToConstant: 100),
            
            checkInStatsStackView.topAnchor.constraint(equalTo: statsStackView.bottomAnchor, constant: 16),
            checkInStatsStackView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            checkInStatsStackView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            checkInStatsStackView.heightAnchor.constraint(equalToConstant: 100),
            
            chartContainerView.topAnchor.constraint(equalTo: checkInStatsStackView.bottomAnchor, constant: 24),
            chartContainerView.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            chartContainerView.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            chartContainerView.heightAnchor.constraint(equalToConstant: 250),
            chartContainerView.bottomAnchor.constraint(equalTo: contentView.bottomAnchor, constant: -24),
            
            chartTitleLabel.topAnchor.constraint(equalTo: chartContainerView.topAnchor, constant: 16),
            chartTitleLabel.leadingAnchor.constraint(equalTo: chartContainerView.leadingAnchor, constant: 16),
            
            chartPlaceholderLabel.centerXAnchor.constraint(equalTo: chartContainerView.centerXAnchor),
            chartPlaceholderLabel.centerYAnchor.constraint(equalTo: chartContainerView.centerYAnchor),
            
            loadingIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            loadingIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
        
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
        scrollView.refreshControl = refreshControl
    }
    
    private func setupBindings() {
        viewModel.onProgressUpdated = { [weak self] stats in
            self?.updateUI(with: stats)
        }
        
        viewModel.onLoadingChanged = { [weak self] isLoading in
            if isLoading {
                self?.loadingIndicator.startAnimating()
            } else {
                self?.loadingIndicator.stopAnimating()
                self?.refreshControl.endRefreshing()
            }
        }
        
        viewModel.onError = { [weak self] message in
            self?.showAlert(title: "错误", message: message)
        }
    }
    
    // MARK: - Data Loading
    
    private func loadProgress() {
        viewModel.loadProgress(planId: planId, userId: userId)
    }
    
    @objc private func refreshData() {
        loadProgress()
    }
    
    // MARK: - UI Update
    
    private func updateUI(with stats: ProgressStats) {
        progressCircleView.setProgress(stats.progressPercentage / 100.0)
        
        currentWeightLabel.text = "当前体重"
        currentWeightValueLabel.text = String(format: "%.1f kg", stats.currentWeight)
        
        initialWeightCard.setValue(String(format: "%.1f kg", stats.initialWeight))
        targetWeightCard.setValue(String(format: "%.1f kg", stats.targetWeight))
        weightLossCard.setValue(String(format: "%.1f kg", stats.weightLoss))
        
        checkInCountCard.setValue("\(stats.checkInCount) 次")
        daysRemainingCard.setValue("\(stats.daysRemaining) 天")
    }
    
    // MARK: - Helper Methods
    
    private func showAlert(title: String, message: String) {
        let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - ProgressCircleView

class ProgressCircleView: UIView {
    
    private let progressLayer = CAShapeLayer()
    private let trackLayer = CAShapeLayer()
    
    private let percentageLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 48, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "完成进度"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    override init(frame: CGRect) {
        super.init(frame: frame)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        super.init(coder: coder)
        setupUI()
    }
    
    private func setupUI() {
        addSubview(percentageLabel)
        addSubview(titleLabel)
        
        NSLayoutConstraint.activate([
            percentageLabel.centerXAnchor.constraint(equalTo: centerXAnchor),
            percentageLabel.centerYAnchor.constraint(equalTo: centerYAnchor, constant: -10),
            
            titleLabel.topAnchor.constraint(equalTo: percentageLabel.bottomAnchor, constant: 4),
            titleLabel.centerXAnchor.constraint(equalTo: centerXAnchor)
        ])
    }
    
    override func layoutSubviews() {
        super.layoutSubviews()
        
        let center = CGPoint(x: bounds.midX, y: bounds.midY)
        let radius = min(bounds.width, bounds.height) / 2 - 10
        let startAngle = -CGFloat.pi / 2
        let endAngle = startAngle + 2 * CGFloat.pi
        
        let circularPath = UIBezierPath(
            arcCenter: center,
            radius: radius,
            startAngle: startAngle,
            endAngle: endAngle,
            clockwise: true
        )
        
        trackLayer.path = circularPath.cgPath
        trackLayer.fillColor = UIColor.clear.cgColor
        trackLayer.strokeColor = UIColor.systemGray5.cgColor
        trackLayer.lineWidth = 15
        trackLayer.lineCap = .round
        
        progressLayer.path = circularPath.cgPath
        progressLayer.fillColor = UIColor.clear.cgColor
        progressLayer.strokeColor = UIColor.systemBlue.cgColor
        progressLayer.lineWidth = 15
        progressLayer.lineCap = .round
        progressLayer.strokeEnd = 0
        
        if trackLayer.superlayer == nil {
            layer.addSublayer(trackLayer)
        }
        if progressLayer.superlayer == nil {
            layer.addSublayer(progressLayer)
        }
    }
    
    func setProgress(_ progress: Double) {
        let clampedProgress = max(0, min(1, progress))
        progressLayer.strokeEnd = CGFloat(clampedProgress)
        percentageLabel.text = String(format: "%.0f%%", clampedProgress * 100)
    }
}

// MARK: - StatCard

class StatCard: UIView {
    
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let valueLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 20, weight: .semibold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    init(title: String) {
        super.init(frame: .zero)
        titleLabel.text = title
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        backgroundColor = .systemBackground
        layer.cornerRadius = 12
        layer.shadowColor = UIColor.black.cgColor
        layer.shadowOpacity = 0.1
        layer.shadowOffset = CGSize(width: 0, height: 2)
        layer.shadowRadius = 4
        
        addSubview(titleLabel)
        addSubview(valueLabel)
        
        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: topAnchor, constant: 16),
            titleLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 8),
            titleLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -8),
            
            valueLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 8),
            valueLabel.leadingAnchor.constraint(equalTo: leadingAnchor, constant: 8),
            valueLabel.trailingAnchor.constraint(equalTo: trailingAnchor, constant: -8),
            valueLabel.bottomAnchor.constraint(lessThanOrEqualTo: bottomAnchor, constant: -16)
        ])
    }
    
    func setValue(_ value: String) {
        valueLabel.text = value
    }
}
