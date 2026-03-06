# PRD: Habit Vibe MVP

## 1. Goal
Help beginners complete daily habits with a low-friction check-in flow.

## 2. Target Users
- Individual learner who wants to build one small daily habit.
- Needs quick logging and visible streak progress.

## 3. Core User Stories
1. As a user, I can create a habit with a title.
2. As a user, I can open a habit detail page and submit a check-in note.
3. As a user, I can see my streak count increase after completion.
4. As a user, my data remains after app restart.

## 4. Scope
### In Scope
- Habit list
- Habit detail
- Add habit form
- Daily completion with note
- Local persistence

### Out of Scope
- Cloud sync
- Account system
- Social sharing

## 5. Screen Flow
1. HabitListView
2. AddHabitView (sheet)
3. HabitDetailView

## 6. Acceptance Criteria
- User can create and view a habit in under 3 taps.
- Completing a habit increments streak immediately.
- App handles empty state and decoding/storage errors.
- Data still visible after app restart.

## 7. Non-functional Requirements
- No crash during common flow.
- All primary state transitions use `AppState`.
- Error messages mapped from `AppError`.
