import SwiftUI

struct AddHabitView: View {
    @Environment(\.dismiss) private var dismiss
    @State private var title = ""

    let onSubmit: (String) -> Void

    var body: some View {
        NavigationStack {
            Form {
                Section("New Habit") {
                    TextField("e.g. Read 20 minutes", text: $title)
                }
            }
            .navigationTitle("Add Habit")
            .toolbar {
                ToolbarItem(placement: .topBarLeading) {
                    Button("Cancel") { dismiss() }
                }
                ToolbarItem(placement: .topBarTrailing) {
                    Button("Save") {
                        onSubmit(title)
                        dismiss()
                    }
                    .disabled(title.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
            }
        }
    }
}
