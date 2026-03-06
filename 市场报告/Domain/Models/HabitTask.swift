import Foundation

struct HabitTask: Identifiable, Codable, Equatable {
    let id: UUID
    var title: String
    var note: String
    var completedDays: Int
    var lastUpdatedAt: Date

    init(
        id: UUID = UUID(),
        title: String,
        note: String = "",
        completedDays: Int = 0,
        lastUpdatedAt: Date = Date()
    ) {
        self.id = id
        self.title = title
        self.note = note
        self.completedDays = completedDays
        self.lastUpdatedAt = lastUpdatedAt
    }
}
