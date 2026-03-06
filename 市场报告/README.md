# iOS Vibe Coding Learning Workspace

This workspace implements a 10-week, 3-4 hours/week plan for learning iOS native vibe coding with a ship-ready MVP target.

## Repository Structure

- `App/`: SwiftUI pages, app entry, navigation, and view models.
- `Domain/`: core business models, types, and use cases.
- `Data/`: API, storage, and repository implementations.
- `Tests/`: unit-test skeletons for key logic and state.
- `Docs/`: weekly plans/reviews, prompts, PRD, and release assets.

## MVP Theme

The first MVP is a **Habit Check-in** app:
- List habits
- View habit details
- Submit check-in notes
- Persist data locally
- Handle loading/error/empty states

## How to Use This Workspace

1. Open this folder in Xcode.
2. Create an iOS App target named `HabitVibe` (SwiftUI lifecycle).
3. Drag folders `App`, `Domain`, `Data`, and `Tests` into the project.
4. Replace the default app entry with `App/HabitVibeApp.swift`.
5. Follow `Docs/weekly/week-01-plan.md` and execute week by week.

## Definition of Done (Week 10)

- TestFlight distributable build available.
- At least one complete user flow verified end-to-end.
- Prompt templates, review checklist, and release checklist all completed.
- Final retrospective completed in `Docs/final-retrospective.md`.
