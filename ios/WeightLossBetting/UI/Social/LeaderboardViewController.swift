import UIKit

class LeaderboardViewController: UIViewController {
    
    // MARK: - UI Components
    
    private let segmentedControl: UISegmentedControl = {
        let items = ["减重榜", "打卡榜", "胜率榜"]
        let control = UISegmentedControl(items: items)
        control.selectedSegmentIndex = 0
        control.translatesAutoresizingMaskIntoConstraints = false
        return control
    }()
    
    private let tableView: UITableView = {
        let table = UITableView()
        table.translatesAutoresizingMaskIntoConstraints = false
        table.register(LeaderboardCell.self, forCellReuseIdentifier: "LeaderboardCell")
        table.rowHeight = 70
        return table
    }()
    
    private let refreshControl = UIRefreshControl()
    
    private let activityIndicator: UIActivityIndicatorView = {
        let indicator = UIActivityIndicatorView(style: .large)
        indicator.translatesAutoresizingMaskIntoConstraints = false
        indicator.hidesWhenStopped = true
        return indicator
    }()
    
    // MARK: - Properties
    
    private let repository = SocialRepository()
    private var leaderboardData: [LeaderboardEntry] = []
    private var currentType: LeaderboardType = .weightLoss
    
    enum LeaderboardType {
        case weightLoss
        case checkInStreak
        case winRate
    }
    
    // MARK: - Lifecycle
    
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        loadLeaderboard()
    }
    
    // MARK: - Setup
    
    private func setupUI() {
        title = "排行榜"
        view.backgroundColor = .systemBackground
        
        view.addSubview(segmentedControl)
        view.addSubview(tableView)
        view.addSubview(activityIndicator)
        
        segmentedControl.addTarget(self, action: #selector(segmentChanged), for: .valueChanged)
        
        tableView.delegate = self
        tableView.dataSource = self
        tableView.refreshControl = refreshControl
        refreshControl.addTarget(self, action: #selector(refreshData), for: .valueChanged)
        
        NSLayoutConstraint.activate([
            segmentedControl.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 16),
            segmentedControl.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
            segmentedControl.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
            
            tableView.topAnchor.constraint(equalTo: segmentedControl.bottomAnchor, constant: 16),
            tableView.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            tableView.trailingAnchor.constraint(equalTo: view.trailingAnchor),
            tableView.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            
            activityIndicator.centerXAnchor.constraint(equalTo: view.centerXAnchor),
            activityIndicator.centerYAnchor.constraint(equalTo: view.centerYAnchor)
        ])
    }
    
    // MARK: - Actions
    
    @objc private func segmentChanged() {
        switch segmentedControl.selectedSegmentIndex {
        case 0:
            currentType = .weightLoss
        case 1:
            currentType = .checkInStreak
        case 2:
            currentType = .winRate
        default:
            break
        }
        loadLeaderboard()
    }
    
    @objc private func refreshData() {
        loadLeaderboard()
    }
    
    // MARK: - Data Loading
    
    private func loadLeaderboard() {
        if !refreshControl.isRefreshing {
            activityIndicator.startAnimating()
        }
        
        let completion: (Result<[LeaderboardEntry], Error>) -> Void = { [weak self] result in
            DispatchQueue.main.async {
                self?.activityIndicator.stopAnimating()
                self?.refreshControl.endRefreshing()
                
                switch result {
                case .success(let entries):
                    self?.leaderboardData = entries
                    self?.tableView.reloadData()
                case .failure(let error):
                    self?.showError(error.localizedDescription)
                }
            }
        }
        
        switch currentType {
        case .weightLoss:
            repository.getWeightLossLeaderboard(completion: completion)
        case .checkInStreak:
            repository.getCheckInStreakLeaderboard(completion: completion)
        case .winRate:
            repository.getWinRateLeaderboard(completion: completion)
        }
    }
    
    private func showError(_ message: String) {
        let alert = UIAlertController(title: "错误", message: message, preferredStyle: .alert)
        alert.addAction(UIAlertAction(title: "确定", style: .default))
        present(alert, animated: true)
    }
}

// MARK: - UITableViewDataSource

extension LeaderboardViewController: UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return leaderboardData.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "LeaderboardCell", for: indexPath) as! LeaderboardCell
        let entry = leaderboardData[indexPath.row]
        cell.configure(with: entry, type: currentType)
        return cell
    }
}

// MARK: - UITableViewDelegate

extension LeaderboardViewController: UITableViewDelegate {
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
    }
}

// MARK: - LeaderboardCell

class LeaderboardCell: UITableViewCell {
    
    private let rankLabel: UILabel = {
        let label = UILabel()
        label.font = .boldSystemFont(ofSize: 20)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let nicknameLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 16)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    private let valueLabel: UILabel = {
        let label = UILabel()
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.textAlignment = .right
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()
    
    override init(style: UITableViewCell.CellStyle, reuseIdentifier: String?) {
        super.init(style: style, reuseIdentifier: reuseIdentifier)
        setupUI()
    }
    
    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }
    
    private func setupUI() {
        contentView.addSubview(rankLabel)
        contentView.addSubview(nicknameLabel)
        contentView.addSubview(valueLabel)
        
        NSLayoutConstraint.activate([
            rankLabel.leadingAnchor.constraint(equalTo: contentView.leadingAnchor, constant: 16),
            rankLabel.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            rankLabel.widthAnchor.constraint(equalToConstant: 40),
            
            nicknameLabel.leadingAnchor.constraint(equalTo: rankLabel.trailingAnchor, constant: 16),
            nicknameLabel.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            
            valueLabel.trailingAnchor.constraint(equalTo: contentView.trailingAnchor, constant: -16),
            valueLabel.centerYAnchor.constraint(equalTo: contentView.centerYAnchor),
            valueLabel.leadingAnchor.constraint(greaterThanOrEqualTo: nicknameLabel.trailingAnchor, constant: 16)
        ])
    }
    
    func configure(with entry: LeaderboardEntry, type: LeaderboardViewController.LeaderboardType) {
        rankLabel.text = "\(entry.rank)"
        nicknameLabel.text = entry.nickname
        
        // Set rank color
        switch entry.rank {
        case 1:
            rankLabel.textColor = .systemYellow
        case 2:
            rankLabel.textColor = .systemGray
        case 3:
            rankLabel.textColor = .systemOrange
        default:
            rankLabel.textColor = .label
        }
        
        // Format value based on type
        switch type {
        case .weightLoss:
            valueLabel.text = String(format: "%.1f kg", entry.value)
        case .checkInStreak:
            valueLabel.text = "\(Int(entry.value)) 天"
        case .winRate:
            valueLabel.text = String(format: "%.1f%%", entry.value * 100)
        }
    }
}
