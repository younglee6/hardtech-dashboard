import Foundation

protocol HabitAPIClient {
    func ping() async -> FeatureResult<Bool>
}

struct MockHabitAPIClient: HabitAPIClient {
    func ping() async -> FeatureResult<Bool> {
        .success(true)
    }
}
