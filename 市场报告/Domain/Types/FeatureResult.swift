import Foundation

enum FeatureResult<T> {
    case success(T)
    case failure(AppError)
}
