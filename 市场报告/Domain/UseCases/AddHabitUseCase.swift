import Foundation

struct AddHabitUseCase {
    private let repository: HabitRepository

    init(repository: HabitRepository) {
        self.repository = repository
    }

    func execute(title: String) -> FeatureResult<HabitTask> {
        let normalized = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !normalized.isEmpty else {
            return .failure(.validation(message: "Title cannot be empty."))
        }

        let habit = HabitTask(title: normalized)
        return repository.add(habit: habit)
    }
}
