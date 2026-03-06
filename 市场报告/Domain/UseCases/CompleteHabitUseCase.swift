import Foundation

struct CompleteHabitUseCase {
    private let repository: HabitRepository

    init(repository: HabitRepository) {
        self.repository = repository
    }

    func execute(id: UUID, note: String) -> FeatureResult<HabitTask> {
        repository.complete(id: id, note: note)
    }
}
