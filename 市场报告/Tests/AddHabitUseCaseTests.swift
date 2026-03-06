import XCTest
@testable import HabitVibe

final class AddHabitUseCaseTests: XCTestCase {
    func testAddHabitFailsWhenTitleEmpty() {
        let repository = InMemoryHabitRepository(seed: [])
        let useCase = AddHabitUseCase(repository: repository)

        let result = useCase.execute(title: "   ")

        switch result {
        case .failure(let error):
            XCTAssertEqual(error, .validation(message: "Title cannot be empty."))
        case .success:
            XCTFail("Expected validation failure")
        }
    }
}
