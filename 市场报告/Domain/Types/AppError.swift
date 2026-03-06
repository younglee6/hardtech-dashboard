import Foundation

enum AppError: Error, Equatable {
    case network(message: String)
    case validation(message: String)
    case system(message: String)
    case unknown

    var displayMessage: String {
        switch self {
        case .network(let message):
            return message
        case .validation(let message):
            return message
        case .system(let message):
            return message
        case .unknown:
            return "Unknown error. Please try again."
        }
    }
}
