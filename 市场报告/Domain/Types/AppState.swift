import Foundation

enum AppState: Equatable {
    case idle
    case loading
    case success
    case error(AppError)
}
