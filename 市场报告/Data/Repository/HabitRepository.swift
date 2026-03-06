import Foundation

protocol HabitRepository {
    func fetch() -> FeatureResult<[HabitTask]>
    func add(habit: HabitTask) -> FeatureResult<HabitTask>
    func complete(id: UUID, note: String) -> FeatureResult<HabitTask>
    func delete(id: UUID) -> FeatureResult<Void>
}

final class DefaultHabitRepository: HabitRepository {
    private let store: HabitStore

    init(store: HabitStore) {
        self.store = store
    }

    func fetch() -> FeatureResult<[HabitTask]> {
        store.loadHabits()
    }

    func add(habit: HabitTask) -> FeatureResult<HabitTask> {
        switch store.loadHabits() {
        case .failure(let error):
            return .failure(error)
        case .success(var habits):
            habits.insert(habit, at: 0)
            switch store.save(habits: habits) {
            case .success:
                return .success(habit)
            case .failure(let error):
                return .failure(error)
            }
        }
    }

    func complete(id: UUID, note: String) -> FeatureResult<HabitTask> {
        switch store.loadHabits() {
        case .failure(let error):
            return .failure(error)
        case .success(var habits):
            guard let index = habits.firstIndex(where: { $0.id == id }) else {
                return .failure(.validation(message: "Habit not found."))
            }

            habits[index].completedDays += 1
            habits[index].note = note
            habits[index].lastUpdatedAt = Date()

            switch store.save(habits: habits) {
            case .success:
                return .success(habits[index])
            case .failure(let error):
                return .failure(error)
            }
        }
    }

    func delete(id: UUID) -> FeatureResult<Void> {
        switch store.loadHabits() {
        case .failure(let error):
            return .failure(error)
        case .success(var habits):
            habits.removeAll { $0.id == id }
            return store.save(habits: habits)
        }
    }
}
