//
//  SettlementViewController.swift
//  WeightLossBetting
//
//  Created by AI Assistant on 2026-03-25.
//

import UIKit

class SettlementViewController: UIViewController {

    // MARK: - Properties
    private let planId: String
    private let opponentName: String
    private let planTitle: String

    private var myAchievement: Bool?
    private var opponentAchievement: Bool?

    // MARK: - UI Elements
    private let titleLabel: UILabel = {
        let label = UILabel()
        label.text = "结算时间到！"
        label.font = .systemFont(ofSize: 24, weight: .bold)
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let subtitleLabel: UILabel = {
        let label = UILabel()
        label.text = "请确认您和对手的减重成果"
        label.font = .systemFont(ofSize: 16)
        label.textColor = .secondaryLabel
        label.textAlignment = .center
        label.numberOfLines = 0
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let mySectionLabel: UILabel = {
        let label = UILabel()
        label.text = "我的减重成果"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let myAchievementSegment: UISegmentedControl = {
        let segment = UISegmentedControl(items: ["未达成", "已达成"])
        segment.selectedSegmentIndex = -1
        segment.translatesAutoresizingMaskIntoConstraints = false
        return segment
    }()

    private let opponentSectionLabel: UILabel = {
        let label = UILabel()
        label.text = "对手的减重成果"
        label.font = .systemFont(ofSize: 18, weight: .semibold)
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    private let opponentAchievementSegment: UISegmentedControl = {
        let segment = UISegmentedControl(items: ["未达成", "已达成"])
        segment.selectedSegmentIndex = -1
        segment.translatesAutoresizingMaskIntoConstraints = false
        return segment
    }()

    private let submitButton: UIButton = {
        let button = UIButton(type: .system)
        button.setTitle("提交结算", for: .normal)
        button.titleLabel?.font = .systemFont(ofSize: 18, weight: .semibold)
        button.backgroundColor = .systemBlue
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = 8
        button.isEnabled = false
        button.translatesAutoresizingMaskIntoConstraints = false
        return button
    }()

    private let noteLabel: UILabel = {
        let label = UILabel()
        label.text = "注意：双方提交的结算结果必须一致，否则将延期结算。"
        label.font = .systemFont(ofSize: 14)
        label.textColor = .secondaryLabel
        label.numberOfLines = 0
        label.textAlignment = .center
        label.translatesAutoresizingMaskIntoConstraints = false
        return label
    }()

    // MARK: - Initialization
    init(planId: String, opponentName: String, planTitle: String) {
        self.planId = planId
        self.opponentName = opponentName
        self.planTitle = planTitle
        super.init(nibName: nil, bundle: nil)
    }

    required init?(coder: NSCoder) {
        fatalError("init(coder:) has not been implemented")
    }

    // MARK: - Lifecycle
    override func viewDidLoad() {
        super.viewDidLoad()
        setupUI()
        setupActions()
    }

    // MARK: - Setup
    private func setupUI() {
        view.backgroundColor = .systemBackground
        title = "结算"

        view.addSubview(titleLabel)
        view.addSubview(subtitleLabel)
        view.addSubview(mySectionLabel)
        view.addSubview(myAchievementSegment)
        view.addSubview(opponentSectionLabel)
        view.addSubview(opponentAchievementSegment)
        view.addSubview(submitButton)
        view.addSubview(noteLabel)

        NSLayoutConstraint.activate([
            titleLabel.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
            titleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            titleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),

            subtitleLabel.topAnchor.constraint(equalTo: titleLabel.bottomAnchor, constant: 10),
            subtitleLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            subtitleLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),

            mySectionLabel.topAnchor.constraint(equalTo: subtitleLabel.bottomAnchor, constant: 40),
            mySectionLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),

            myAchievementSegment.topAnchor.constraint(equalTo: mySectionLabel.bottomAnchor, constant: 10),
            myAchievementSegment.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            myAchievementSegment.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            myAchievementSegment.heightAnchor.constraint(equalToConstant: 40),

            opponentSectionLabel.topAnchor.constraint(equalTo: myAchievementSegment.bottomAnchor, constant: 30),
            opponentSectionLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),

            opponentAchievementSegment.topAnchor.constraint(equalTo: opponentSectionLabel.bottomAnchor, constant: 10),
            opponentAchievementSegment.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            opponentAchievementSegment.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            opponentAchievementSegment.heightAnchor.constraint(equalToConstant: 40),

            submitButton.topAnchor.constraint(equalTo: opponentAchievementSegment.bottomAnchor, constant: 40),
            submitButton.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            submitButton.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
            submitButton.heightAnchor.constraint(equalToConstant: 50),

            noteLabel.topAnchor.constraint(equalTo: submitButton.bottomAnchor, constant: 20),
            noteLabel.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 20),
            noteLabel.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -20),
        ])
    }

    private func setupActions() {
        myAchievementSegment.addTarget(self, action: #selector(segmentChanged), for: .valueChanged)
        opponentAchievementSegment.addTarget(self, action: #selector(segmentChanged), for: .valueChanged)
        submitButton.addTarget(self, action: #selector(submitSettlement), for: .touchUpInside)
    }

    // MARK: - Actions
    @objc private func segmentChanged() {
        myAchievement = myAchievementSegment.selectedSegmentIndex == 1
        opponentAchievement = opponentAchievementSegment.selectedSegmentIndex == 1

        submitButton.isEnabled = myAchievement != nil && opponentAchievement != nil
    }

    @objc private func submitSettlement() {
        guard let myAchievement = myAchievement,
              let opponentAchievement = opponentAchievement else { return }

        submitButton.isEnabled = false
        submitButton.setTitle("提交中...", for: .disabled)

        SettlementService.shared.submitSettlementClaim(
            planId: planId,
            myAchievement: myAchievement,
            opponentAchievement: opponentAchievement
        ) { [weak self] result in
            DispatchQueue.main.async {
                self?.submitButton.isEnabled = true
                self?.submitButton.setTitle("提交结算", for: .normal)

                switch result {
                case .success:
                    let alert = UIAlertController(
                        title: "结算提交成功",
                        message: "您的结算结果已提交，等待对手确认。",
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "确定", style: .default) { [weak self] _ in
                        self?.navigationController?.popViewController(animated: true)
                    })
                    self?.present(alert, animated: true)

                case .failure(let error):
                    let alert = UIAlertController(
                        title: "提交失败",
                        message: error.localizedDescription,
                        preferredStyle: .alert
                    )
                    alert.addAction(UIAlertAction(title: "重试", style: .default))
                    self?.present(alert, animated: true)
                }
            }
        }
    }
}
