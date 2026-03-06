# Prompt Template: Implementation Design

You are a staff iOS engineer.

Context:
- Stack: Swift + SwiftUI
- Architecture folders: App / Domain / Data / Tests
- Required types: UserAction, AppState, FeatureResult<T>, AppError

Task:
- Provide a step-by-step implementation plan for this feature.
- Include file-level changes and data flow.

Feature:
{{paste feature}}

Output format:
1. Proposed data flow
2. Files to create/update
3. Key Swift types/signatures
4. Failure handling
5. Minimal test cases
