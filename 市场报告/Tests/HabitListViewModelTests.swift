import XCTest
@testable import HabitVibe

@MainActor
final class HabitListViewModelTests: XCTestCase {
    func testLoadSetsSuccessAndReturnsHabits() {
        let seed = [HabitTask(title: "Read")] 
        let repository = InMemoryHabitRepository(seed: seed)
        let viewModel = HabitListViewModel(repository: repository)

        viewModel.load()

        XCTAssertEqual(viewModel.state, .success)
        XCTAssertEqual(viewModel.habits.count, 1)
    }
}
