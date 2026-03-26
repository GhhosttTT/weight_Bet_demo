import Foundation

class PaymentMethodViewModel {
    private let userRepository = UserRepository.shared
    
    // MARK: - Bind Payment Method
    
    func bindPaymentMethod(
        userId: String,
        cardNumber: String,
        expiry: String,
        cvv: String,
        cardHolder: String,
        completion: @escaping (Result<Void, Error>) -> Void
    ) {
        // Validate card number (basic validation)
        let cleanedCardNumber = cardNumber.replacingOccurrences(of: " ", with: "")
        guard cleanedCardNumber.count >= 13 && cleanedCardNumber.count <= 19 else {
            completion(.failure(PaymentError.invalidCardNumber))
            return
        }
        
        // Validate expiry format (MM/YY)
        let expiryComponents = expiry.split(separator: "/")
        guard expiryComponents.count == 2,
              let month = Int(expiryComponents[0]),
              let year = Int(expiryComponents[1]),
              month >= 1 && month <= 12 else {
            completion(.failure(PaymentError.invalidExpiry))
            return
        }
        
        // Validate CVV
        guard cvv.count >= 3 && cvv.count <= 4 else {
            completion(.failure(PaymentError.invalidCVV))
            return
        }
        
        // Validate cardholder name
        guard cardHolder.count >= 2 else {
            completion(.failure(PaymentError.invalidCardHolder))
            return
        }
        
        // Build parameters
        // Note: In production, you should tokenize the card using Stripe SDK
        // and send only the token to the backend
        let parameters: [String: Any] = [
            "card_number": cleanedCardNumber,
            "expiry_month": month,
            "expiry_year": year,
            "cvv": cvv,
            "cardholder_name": cardHolder
        ]
        
        // Bind payment method
        userRepository.bindPaymentMethod(userId: userId, parameters: parameters, completion: completion)
    }
}

// MARK: - Payment Errors

enum PaymentError: LocalizedError {
    case invalidCardNumber
    case invalidExpiry
    case invalidCVV
    case invalidCardHolder
    
    var errorDescription: String? {
        switch self {
        case .invalidCardNumber:
            return "Invalid card number"
        case .invalidExpiry:
            return "Invalid expiry date (use MM/YY format)"
        case .invalidCVV:
            return "Invalid CVV (3 or 4 digits)"
        case .invalidCardHolder:
            return "Invalid cardholder name"
        }
    }
}
