import SwiftUI

struct HabitListView: View {
    @StateObject private var viewModel: HabitListViewModel
    @State private var showAddSheet = false

    init(viewModel: HabitListViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }

    var body: some View {
        NavigationStack {
            Group {
                switch viewModel.state {
                case .idle, .loading:
                    ProgressView("Loading habits...")
                case .error(let error):
                    VStack(spacing: 12) {
                        Text(error.displayMessage)
                            .multilineTextAlignment(.center)
                        Button("Retry") {
                            viewModel.load()
                        }
                    }
                    .padding()
                case .success:
                    if viewModel.habits.isEmpty {
                        ContentUnavailableView(
                            "No habits yet",
                            systemImage: "checklist",
                            description: Text("Tap + to add your first habit.")
                        )
                    } else {
                        List(viewModel.habits) { habit in
                            NavigationLink {
                                HabitDetailView(habit: habit) { note in
                                    viewModel.completeHabit(id: habit.id, note: note)
                                }
                            } label: {
                                HStack {
                                    VStack(alignment: .leading) {
                                        Text(habit.title)
                                            .font(.headline)
                                        Text("Streak: \(habit.completedDays)")
                                            .font(.caption)
                                            .foregroundStyle(.secondary)
                                    }
                                    Spacer()
                                    Image(systemName: "chevron.right")
                                        .foregroundStyle(.tertiary)
                                }
                            }
                        }
                    }
                }
            }
            .navigationTitle("Habit Vibe")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        showAddSheet = true
                    } label: {
                        Image(systemName: "plus")
                    }
                }
            }
            .sheet(isPresented: $showAddSheet) {
                AddHabitView { title in
                    viewModel.addHabit(title: title)
                }
            }
            .onAppear {
                viewModel.load()
            }
        }
    }
}
