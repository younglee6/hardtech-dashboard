import Foundation

protocol HabitStore {
    func loadHabits() -> FeatureResult<[HabitTask]>
    func save(habits: [HabitTask]) -> FeatureResult<Void>
}

final class UserDefaultsHabitStore: HabitStore {
    private let key = "habit_vibe_tasks"
    private let defaults: UserDefaults

    init(defaults: UserDefaults = .standard) {
        self.defaults = defaults
    }

    func loadHabits() -> FeatureResult<[HabitTask]> {
        guard let data = defaults.data(forKey: key) else {
            return .success([])
        }

        do {
            let habits = try JSONDecoder().decode([HabitTask].self, from: data)
            return .success(habits)
        } catch {
            return .failure(.system(message: "Failed to decode local habits."))
        }
    }

    func save(habits: [HabitTask]) -> FeatureResult<Void> {
        do {
            let data = try JSONEncoder().encode(habits)
            defaults.set(data, forKey: key)
            return .success(())
        } catch {
            return .failure(.system(message: "Failed to save habits locally."))
        }
    }
}
