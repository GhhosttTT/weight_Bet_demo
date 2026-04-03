import Foundation

enum ValidationError: Error {
    case invalidEmail
    case passwordTooShort
    case passwordsDoNotMatch
    case nicknameTooShort
    case custom(String)
    
    var errorDescription: String? {
        switch self {
        case .invalidEmail:
            return "请输入有效的邮箱地址"
        case .passwordTooShort:
            return "密码至少需要6个字符"
        case .passwordsDoNotMatch:
            return "密码不匹配"
        case .nicknameTooShort:
            return "昵称至少需要2个字符"
        case .custom(let message):
            return message
        }
    }
}
