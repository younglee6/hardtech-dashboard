import Foundation

@MainActor
final class HabitListViewModel: ObservableObject {
    @Published private(set) var state: AppState = .idle
    @Published private(set) var habits: [HabitTask] = []

    private let repository: HabitRepository
    private lazy var addUseCase = AddHabitUseCase(repository: repository)
    private lazy var completeUseCase = CompleteHabitUseCase(repository: repository)

    init(repository: HabitRepository) {
        self.repository = repository
    }

    func load() {
        state = .loading
        switch repository.fetch() {
        case .success(let habits):
            self.habits = habits
            state = .success
        case .failure(let error):
            state = .error(error)
        }
    }

    func addHabit(title: String) {
        switch addUseCase.execute(title: title) {
        case .success:
            load()
        case .failure(let error):
            state = .error(error)
        }
    }

    func completeHabit(id: UUID, note: String) {
        switch completeUseCase.execute(id: id, note: note) {
        case .success:
            load()
        case .failure(let error):
            state = .error(error)
        }
    }

    func deleteHabit(id: UUID) {
        switch repository.delete(id: id) {
        case .success:
            load()
        case .failure(let error):
            state = .error(error)
        }
    }
}
