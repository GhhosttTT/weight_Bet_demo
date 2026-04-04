import UIKit
import StoreKit
import Toast_Swift

class BalanceViewController: UIViewController {
    @IBOutlet weak var balanceLabel: UILabel! // Balance label
    @IBOutlet weak var historyTableView: UITableView! // Transaction history table
    @IBOutlet weak var chargeButton: UIButton! // Charge button
    @IBOutlet weak var withdrawButton: UIButton! // Withdraw button
    @IBOutlet weak var loadingIndicator: UIActivityIndicatorView! // Loading indicator
    @IBOutlet weak var loadingOverlayView: UIView! // Loading overlay view
    
    let viewModel = BalanceViewModel()
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        setupUI()
        setupBindings()
        loadData()
    }
    
    override func viewWillAppear(_ animated: Bool) {
        super.viewWillAppear(animated)
        loadData()
    }
    
    // Set up UI
    func setupUI() {
        title = "我的余额"
        
        // 设置按钮样式 - 使用渐变蓝色，更加协调
        chargeButton.layer.cornerRadius = 10
        chargeButton.backgroundColor = UIColor.systemBlue
        chargeButton.setTitleColor(.white, for: .normal)
        chargeButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        
        withdrawButton.layer.cornerRadius = 10
        withdrawButton.backgroundColor = UIColor.systemGreen
        withdrawButton.setTitleColor(.white, for: .normal)
        withdrawButton.titleLabel?.font = UIFont.systemFont(ofSize: 16, weight: .semibold)
        
        // 设置按钮阴影效果
        [chargeButton, withdrawButton].forEach { button in
            button.layer.shadowColor = UIColor.black.cgColor
            button.layer.shadowOffset = CGSize(width: 0, height: 2)
            button.layer.shadowOpacity = 0.15
            button.layer.shadowRadius = 4
        }
        
        historyTableView.delegate = self
        historyTableView.dataSource = self
        historyTableView.separatorStyle = .singleLine
        historyTableView.rowHeight = 90
        
        loadingIndicator.isHidden = true
        loadingOverlayView.isHidden = true
        
        let refreshControl = UIRefreshControl()
        refreshControl.addTarget(self, action: #selector(loadData), for: .valueChanged)
        historyTableView.refreshControl = refreshControl
    }
    
    // Set up bindings
    func setupBindings() {
        viewModel.onBalanceStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                switch state {
                case .success(let balance):
                    self?.updateBalanceDisplay(balance: balance.availableBalance)
                case .error(let error):
                    self?.view.makeToast(error, duration: 3.0, position: .bottom)
                case .loading:
                    break
                case .idle:
                    break
                }
                
                self?.loadingIndicator.isHidden = true
                self?.loadingOverlayView.isHidden = true
            }
        }
        
        viewModel.onTransactionsStateChanged = { [weak self] state in
            DispatchQueue.main.async {
                switch state {
                case .success(_):
                    self?.historyTableView.reloadData()
                    self?.historyTableView.refreshControl?.endRefreshing()
                case .error(let error):
                    self?.view.makeToast(error, duration: 3.0, position: .bottom)
                case .loading:
                    break
                case .idle:
                    break
                }
            }
        }
    }
    
    // Load data
    @objc func loadData() {
        loadingIndicator.isHidden = false
        loadingOverlayView.isHidden = false
        loadingIndicator.startAnimating()
        
        viewModel.fetchData()
    }
    
    // Update balance display
    func updateBalanceDisplay(balance: Double) {
        let numberFormatter = NumberFormatter()
        numberFormatter.numberStyle = .currency
        numberFormatter.currencySymbol = "¥"
        numberFormatter.minimumFractionDigits = 2
        numberFormatter.maximumFractionDigits = 2
        
        let balanceString = numberFormatter.string(from: NSNumber(value: balance))
        balanceLabel.text = balanceString
    }
    
    // Charge button tapped event
    @IBAction func chargeButtonTapped(_ sender: Any) {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        let chargeVC = storyboard.instantiateViewController(withIdentifier: "ChargeViewController") as! ChargeViewController
        navigationController?.pushViewController(chargeVC, animated: true)
    }
    
    // Show charge page with pre-filled amount
    func showChargePage(withAmount amount: Double) {
        let chargeVC = ChargeViewController()
        chargeVC.preFillAmount(amount)
        navigationController?.pushViewController(chargeVC, animated: true)
    }
    
    // Withdraw button tapped event
    @IBAction func withdrawButtonTapped(_ sender: Any) {
        let storyboard = UIStoryboard(name: "Main", bundle: nil)
        let withdrawVC = storyboard.instantiateViewController(withIdentifier: "WithdrawViewController") as! WithdrawViewController
        navigationController?.pushViewController(withdrawVC, animated: true)
    }
}

// Table view extension
extension BalanceViewController: UITableViewDelegate, UITableViewDataSource {
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        // 由于我们没有直接访问 transactions 的属性，我们需要存储一份本地副本
        // 这里我们需要修改 BalanceViewModel 来提供访问方法，或者存储本地副本
        // 为了简化，我们先添加本地属性来存储数据
        // 不过我们需要先检查 BalanceViewModel 的状态
        switch viewModel.transactionsState {
        case .success(let transactions):
            return transactions.count
        default:
            return 0
        }
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier: "TransactionCell", for: indexPath) as! TransactionTableViewCell
        
        switch viewModel.transactionsState {
        case .success(let transactions):
            let transaction = transactions[indexPath.row]
            cell.configure(transaction: transaction)
        default:
            break
        }
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
    }
    
    func tableView(_ tableView: UITableView, titleForHeaderInSection section: Int) -> String? {
        switch viewModel.transactionsState {
        case .success(let transactions):
            if transactions.count > 0 {
                return "Transaction History"
            }
        default:
            break
        }
        return nil
    }
}

// Transaction history table view cell
class TransactionTableViewCell: UITableViewCell {
    @IBOutlet weak var transactionTypeLabel: UILabel! // Transaction type label
    @IBOutlet weak var transactionAmountLabel: UILabel! // Transaction amount label
    @IBOutlet weak var transactionDateLabel: UILabel! // Transaction date label
    @IBOutlet weak var transactionStatusLabel: UILabel! // Transaction status label
    
    func configure(transaction: Transaction) {
        // 处理 TransactionType
        switch transaction.type {
        case .freeze:
            transactionTypeLabel.text = "Freeze"
        case .unfreeze:
            transactionTypeLabel.text = "Unfreeze"
        case .transfer:
            transactionTypeLabel.text = "Transfer"
        case .withdraw:
            transactionTypeLabel.text = "Withdraw"
        case .refund:
            transactionTypeLabel.text = "Refund"
        }
        
        // 处理金额显示
        let amountSign = transaction.type == .refund || transaction.type == .unfreeze ? "+" : "-"
        transactionAmountLabel.text = amountSign + "¥" + String(format: "%.2f", abs(transaction.amount))
        transactionAmountLabel.textColor = (transaction.type == .refund || transaction.type == .unfreeze) ? .systemGreen : .systemRed
        
        // 处理日期格式化
        transactionDateLabel.text = formatDate(date: transaction.createdAt)
        
        // 处理 TransactionStatus
        switch transaction.status {
        case .pending:
            transactionStatusLabel.text = "Processing"
            transactionStatusLabel.textColor = .systemOrange
        case .completed:
            transactionStatusLabel.text = "Completed"
            transactionStatusLabel.textColor = .systemGreen
        case .failed:
            transactionStatusLabel.text = "Failed"
            transactionStatusLabel.textColor = .systemRed
        }
    }
    
    func formatDate(date: Date) -> String {
        let formatter = DateFormatter()
        formatter.dateFormat = "MM-dd HH:mm"
        return formatter.string(from: date)
    }
}