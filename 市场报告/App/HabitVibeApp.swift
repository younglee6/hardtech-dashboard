import SwiftUI

@main
struct HabitVibeApp: App {
    var body: some Scene {
        WindowGroup {
            let store = UserDefaultsHabitStore()
            let repository = DefaultHabitRepository(store: store)
            HabitListView(viewModel: HabitListViewModel(repository: repository))
        }
    }
}
