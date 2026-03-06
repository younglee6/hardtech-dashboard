import Foundation
@testable import HabitVibe

final class InMemoryHabitRepository: HabitRepository {
    private var items: [HabitTask]

    init(seed: [HabitTask]) {
        self.items = seed
    }

    func fetch() -> FeatureResult<[HabitTask]> {
        .success(items)
    }

    func add(habit: HabitTask) -> FeatureResult<HabitTask> {
        items.insert(habit, at: 0)
        return .success(habit)
    }

    func complete(id: UUID, note: String) -> FeatureResult<HabitTask> {
        guard let index = items.firstIndex(where: { $0.id == id }) else {
            return .failure(.validation(message: "Habit not found."))
        }
        items[index].completedDays += 1
        items[index].note = note
        return .success(items[index])
    }

    func delete(id: UUID) -> FeatureResult<Void> {
        items.removeAll { $0.id == id }
        return .success(())
    }
}
