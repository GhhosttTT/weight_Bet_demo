import UIKit

/// Application theme configuration
struct AppTheme {
    
    // MARK: - Colors
    
    struct Colors {
        static let primary = UIColor(red: 0.592, green: 0.373, blue: 0.988, alpha: 1.0)
        static let primaryLight = UIColor(red: 0.702, green: 0.514, blue: 0.992, alpha: 1.0)
        static let primaryDark = UIColor(red: 0.455, green: 0.227, blue: 0.851, alpha: 1.0)
        static let secondary = UIColor.systemGreen
        static let accent = UIColor.systemOrange
        static let error = UIColor.systemRed
        static let warning = UIColor.systemYellow
        static let success = UIColor.systemGreen
        
        static let background = UIColor.systemBackground
        static let secondaryBackground = UIColor.secondarySystemBackground
        static let tertiaryBackground = UIColor.tertiarySystemBackground
        
        static let label = UIColor.label
        static let secondaryLabel = UIColor.secondaryLabel
        static let tertiaryLabel = UIColor.tertiaryLabel
        
        static let separator = UIColor.separator
    }
    
    // MARK: - Fonts
    
    struct Fonts {
        static func largeTitle() -> UIFont {
            return .systemFont(ofSize: 34, weight: .bold)
        }
        
        static func title1() -> UIFont {
            return .systemFont(ofSize: 28, weight: .bold)
        }
        
        static func title2() -> UIFont {
            return .systemFont(ofSize: 22, weight: .bold)
        }
        
        static func title3() -> UIFont {
            return .systemFont(ofSize: 20, weight: .semibold)
        }
        
        static func headline() -> UIFont {
            return .systemFont(ofSize: 17, weight: .semibold)
        }
        
        static func body() -> UIFont {
            return .systemFont(ofSize: 17, weight: .regular)
        }
        
        static func callout() -> UIFont {
            return .systemFont(ofSize: 16, weight: .regular)
        }
        
        static func subheadline() -> UIFont {
            return .systemFont(ofSize: 15, weight: .regular)
        }
        
        static func footnote() -> UIFont {
            return .systemFont(ofSize: 13, weight: .regular)
        }
        
        static func caption1() -> UIFont {
            return .systemFont(ofSize: 12, weight: .regular)
        }
        
        static func caption2() -> UIFont {
            return .systemFont(ofSize: 11, weight: .regular)
        }
    }
    
    // MARK: - Spacing
    
    struct Spacing {
        static let tiny: CGFloat = 4
        static let small: CGFloat = 8
        static let medium: CGFloat = 16
        static let large: CGFloat = 24
        static let extraLarge: CGFloat = 32
    }
    
    // MARK: - Corner Radius
    
    struct CornerRadius {
        static let small: CGFloat = 8
        static let medium: CGFloat = 12
        static let large: CGFloat = 16
        static let extraLarge: CGFloat = 24
    }
    
    // MARK: - Shadow
    
    struct Shadow {
        static func small() -> (color: UIColor, opacity: Float, offset: CGSize, radius: CGFloat) {
            return (UIColor.black, 0.1, CGSize(width: 0, height: 2), 4)
        }
        
        static func medium() -> (color: UIColor, opacity: Float, offset: CGSize, radius: CGFloat) {
            return (UIColor.black, 0.15, CGSize(width: 0, height: 4), 8)
        }
        
        static func large() -> (color: UIColor, opacity: Float, offset: CGSize, radius: CGFloat) {
            return (UIColor.black, 0.2, CGSize(width: 0, height: 8), 16)
        }
    }
    
    // MARK: - Apply Theme
    
    static func apply() {
        // Navigation Bar
        let navigationBarAppearance = UINavigationBarAppearance()
        navigationBarAppearance.configureWithOpaqueBackground()
        navigationBarAppearance.backgroundColor = Colors.background
        navigationBarAppearance.titleTextAttributes = [
            .foregroundColor: Colors.label,
            .font: Fonts.headline()
        ]
        navigationBarAppearance.largeTitleTextAttributes = [
            .foregroundColor: Colors.label,
            .font: Fonts.largeTitle()
        ]
        
        UINavigationBar.appearance().standardAppearance = navigationBarAppearance
        UINavigationBar.appearance().compactAppearance = navigationBarAppearance
        UINavigationBar.appearance().tintColor = Colors.primary
        
        if #available(iOS 15.0, *) {
            UINavigationBar.appearance().scrollEdgeAppearance = navigationBarAppearance
        }
        
        // Tab Bar
        let tabBarAppearance = UITabBarAppearance()
        tabBarAppearance.configureWithOpaqueBackground()
        tabBarAppearance.backgroundColor = Colors.background
        
        UITabBar.appearance().standardAppearance = tabBarAppearance
        if #available(iOS 15.0, *) {
            UITabBar.appearance().scrollEdgeAppearance = tabBarAppearance
        }
        UITabBar.appearance().tintColor = Colors.primary
        UITabBar.appearance().unselectedItemTintColor = Colors.secondaryLabel
        
        // Table View
        UITableView.appearance().backgroundColor = Colors.background
        UITableView.appearance().separatorColor = Colors.separator
        
        // Collection View
        UICollectionView.appearance().backgroundColor = Colors.background
        
        // Text Field
        UITextField.appearance().tintColor = Colors.primary
        
        // Text View
        UITextView.appearance().tintColor = Colors.primary
        
        // Switch
        UISwitch.appearance().onTintColor = Colors.primary
        
        // Activity Indicator
        UIActivityIndicatorView.appearance().color = Colors.primary
    }
}

// MARK: - UIView Extension

extension UIView {
    
    /// Apply shadow to view
    func applyShadow(style: (color: UIColor, opacity: Float, offset: CGSize, radius: CGFloat)) {
        layer.shadowColor = style.color.cgColor
        layer.shadowOpacity = style.opacity
        layer.shadowOffset = style.offset
        layer.shadowRadius = style.radius
        layer.masksToBounds = false
    }
    
    /// Apply corner radius
    func applyCornerRadius(_ radius: CGFloat) {
        layer.cornerRadius = radius
        layer.masksToBounds = true
    }
    
    /// Apply border
    func applyBorder(color: UIColor, width: CGFloat) {
        layer.borderColor = color.cgColor
        layer.borderWidth = width
    }
}

// MARK: - UIButton Extension

extension UIButton {
    
    /// Create a primary button
    static func primaryButton(title: String) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        button.titleLabel?.font = AppTheme.Fonts.headline()
        button.backgroundColor = AppTheme.Colors.primary
        button.setTitleColor(.white, for: .normal)
        button.layer.cornerRadius = AppTheme.CornerRadius.medium
        button.contentEdgeInsets = UIEdgeInsets(
            top: AppTheme.Spacing.medium,
            left: AppTheme.Spacing.large,
            bottom: AppTheme.Spacing.medium,
            right: AppTheme.Spacing.large
        )
        return button
    }
    
    /// Create a secondary button
    static func secondaryButton(title: String) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        button.titleLabel?.font = AppTheme.Fonts.headline()
        button.backgroundColor = AppTheme.Colors.secondaryBackground
        button.setTitleColor(AppTheme.Colors.primary, for: .normal)
        button.layer.cornerRadius = AppTheme.CornerRadius.medium
        button.contentEdgeInsets = UIEdgeInsets(
            top: AppTheme.Spacing.medium,
            left: AppTheme.Spacing.large,
            bottom: AppTheme.Spacing.medium,
            right: AppTheme.Spacing.large
        )
        return button
    }
    
    /// Create a text button
    static func textButton(title: String) -> UIButton {
        let button = UIButton(type: .system)
        button.setTitle(title, for: .normal)
        button.titleLabel?.font = AppTheme.Fonts.body()
        button.setTitleColor(AppTheme.Colors.primary, for: .normal)
        return button
    }
}

// MARK: - Dark Mode Support

extension AppTheme {
    
    /// Check if dark mode is enabled
    static var isDarkMode: Bool {
        if #available(iOS 13.0, *) {
            return UITraitCollection.current.userInterfaceStyle == .dark
        }
        return false
    }
    
    /// Toggle dark mode (iOS 13+)
    @available(iOS 13.0, *)
    static func setDarkMode(_ enabled: Bool) {
        guard let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene else {
            return
        }
        
        windowScene.windows.forEach { window in
            window.overrideUserInterfaceStyle = enabled ? .dark : .light
        }
    }
}
