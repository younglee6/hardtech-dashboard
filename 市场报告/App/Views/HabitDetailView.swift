import SwiftUI

struct HabitDetailView: View {
    let habit: HabitTask
    let onCheckIn: (String) -> Void

    @State private var note = ""

    var body: some View {
        Form {
            Section("Habit") {
                Text(habit.title)
                Text("Current streak: \(habit.completedDays)")
                    .foregroundStyle(.secondary)
            }

            Section("Check-in Note") {
                TextField("What helped you today?", text: $note)
                Button("Complete Today") {
                    onCheckIn(note)
                }
                .buttonStyle(.borderedProminent)
            }
        }
        .navigationTitle("Habit Detail")
    }
}
