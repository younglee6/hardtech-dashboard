import Foundation

enum UserAction: Equatable {
    case loadHabits
    case addHabit(title: String)
    case completeHabit(id: UUID, note: String)
    case deleteHabit(id: UUID)
}
