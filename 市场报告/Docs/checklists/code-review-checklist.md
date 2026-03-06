# Code Review Checklist

## Correctness
- [ ] All user actions map to expected state transitions.
- [ ] `AppState` changes are deterministic and observable.
- [ ] Error paths return `AppError` consistently.

## Stability
- [ ] No force unwrap in production paths.
- [ ] Empty/invalid input is validated.
- [ ] Network/storage failures are surfaced to UI.

## Architecture
- [ ] UI logic stays in ViewModel, not in View.
- [ ] Domain and Data layers are not bypassed.
- [ ] New feature follows `App/Domain/Data/Tests` folder contract.

## Test Coverage
- [ ] Core use case has unit tests.
- [ ] At least one failure scenario is tested.
- [ ] Regression risk areas are listed.
