# SikuliFramework to SikuliGO Python Migration Plan

## 1. Objective
Migrate `sikuli-framework` from a Jython/SikuliX Java runtime to a CPython 3 runtime backed by the `sikuligo` Python client, while preserving the framework's object model, baseline conventions, and Robot Framework keyword experience.

## 2. Success Criteria
- Existing framework maps (calculator/textedit style) run on CPython 3 without Java Sikuli imports.
- Core interaction paths (`find`, `exists`, `wait`, `click`, `type`, drag/drop where supported) execute through `sikuligo`.
- Robot Framework keywords remain stable in naming and behavior for common usage.
- Baseline image naming and search semantics remain compatible.
- CI executes framework tests against a real `sikuligo` server (manual and auto-launch modes).

## 3. Current-State Constraints (Must Address)
- Runtime is Python 2 + Jython assumptions.
- Hard imports to Java classes and SikuliX modules in:
  - `src/bootstrap.py`
  - `src/config.py`
  - `src/wrapper.py`
  - `src/region/finder.py`
  - `src/region/transform.py`
  - `src/entity/*`
  - `src/robotframework/*`
- Finder/transform behavior is tightly coupled to SikuliX `Region`, `Pattern`, `Location`, and `FindFailed`.
- Input control currently uses Java `InputEvent` and direct mouse down/up.

## 4. Target Architecture
- **Execution backend**: `sikuligo` package (`Screen`, `Pattern`, `Sikuli`).
- **Compatibility layer**: new adapter API inside framework so higher layers do not call SikuliX/Jython types directly.
- **Framework core** (`entity`, `finder`, `transform`, `robotframework`) uses adapter interfaces only.
- **Backend selection**: temporary toggle during migration (`SIKULI_FRAMEWORK_BACKEND=sikuligo|legacy`) to allow stepwise cutover.

## 5. Detailed Workstreams

## Workstream 0: Migration Baseline and Branch Hygiene
### Scope
Create a repeatable baseline and lock migration assumptions.

### Tasks
1. Add migration doc and checklist (this file + tracking issue).
2. Snapshot current examples and expected outcomes.
3. Define minimum supported versions:
   - Python 3.10+
   - `sikuligo` version target
4. Add backend feature matrix (legacy vs sikuligo).

### Deliverables
- `docs/migration-sikuligo-python-plan.md`
- `docs/migration-feature-matrix.md` (new)

### Exit Criteria
- Team has explicit parity list and non-goals before code rewrites start.

## Workstream 1: Runtime Modernization (Python 3)
### Scope
Make framework importable and testable on CPython 3.

### Tasks
1. Python 2 to 3 syntax conversion across `src/`:
   - `except Exception, e` -> `except Exception as e`
   - `unicode` handling replacements
   - `md5` module import replacement (`hashlib`)
2. Replace Jython-only constructs (`execfile`, Java package assumptions) with Python 3 equivalents.
3. Add package metadata (`pyproject.toml` or equivalent) for local install/test.
4. Add dev tooling:
   - formatter/linter (optional but recommended)
   - pytest config

### Deliverables
- Python 3 compatible source tree.
- Test bootstrap script for local developer setup.

### Exit Criteria
- `python -m pytest` runs test discovery without syntax/runtime import crashes.

## Workstream 2: Backend Adapter Layer
### Scope
Create an abstraction that mirrors needed Sikuli behavior but uses `sikuligo` calls underneath.

### Tasks
1. Add adapter package, for example:
   - `src/adapters/sikuligo_backend.py`
   - `src/adapters/types.py`
2. Define adapter interfaces:
   - `BackendScreen`
   - `BackendRegion`
   - `BackendPattern`
   - `BackendMatch`
3. Implement first backend using:
   - `from sikuligo import Screen, Pattern`
4. Add conversion/error mapping:
   - gRPC/`SikuliError` -> framework exceptions
5. Add bootstrap wiring:
   - Configure `Config.screen` via adapter, not SikuliX import.

### Deliverables
- Working adapter with core primitives.

### Exit Criteria
- Simple smoke script can instantiate screen and execute `find`/`click` through adapter.

## Workstream 3: Finder and Transform Migration
### Scope
Move image lookup and matching flow to adapter-backed execution while preserving naming strategy.

### Tasks
1. Refactor `src/region/finder.py`:
   - remove `org.sikuli.*` dependencies
   - keep baseline resolution rules (`single`, `sequence`, `series`, `series-sequence`)
   - call adapter region operations for matching
2. Refactor `src/region/transform.py`:
   - route pattern transforms to adapter pattern object
   - replace location/region manipulations with backend-neutral structures
3. Implement equivalent timeout/retry semantics and interval behavior.

### Deliverables
- Adapter-native finder/transform modules.

### Exit Criteria
- Existing baseline sets resolve and match using `sikuligo` backend.

## Workstream 4: Entity/Interaction Layer Migration
### Scope
Replace direct Java/SikuliX input APIs in entity behaviors.

### Tasks
1. Refactor `src/entity/clickStrategy.py`:
   - remove `InputEvent` dependency
   - map left/right click to backend methods
2. Refactor `src/entity/entities/clickableEntity.py` and related classes:
   - ensure click/drag/type use backend operations
3. Refactor text entry classes (`textBox.py`, others) to backend typing API.
4. Implement fallback behavior where parity is unavailable (explicit error + feature flag).

### Deliverables
- Entity actions fully backend-driven.

### Exit Criteria
- Calculator and textedit examples execute with real interaction flow on `sikuligo`.

## Workstream 5: Logging, Capture, and Diagnostics
### Scope
Preserve debugging/reporting UX currently built around local capture/log hooks.

### Tasks
1. Replace capture paths that depend on SikuliX capture utilities.
2. Map screenshot capture for formatter outputs (`src/log/formatter.py`).
3. Preserve result asset storage contract (`results/assets`).
4. Add request/trace ID propagation hooks where available.

### Deliverables
- Functional logs with image links in reports.

### Exit Criteria
- Log output still includes useful visual artifacts for failed assertions.

## Workstream 6: Robot Framework Compatibility
### Scope
Keep RF keyword surface stable while swapping execution backend.

### Tasks
1. Refactor `src/robotframework/sikuliFwRfAbstractLib.py` to use migrated framework APIs.
2. Validate keyword behavior for:
   - launch/select/click/type/assert
3. Add regression suite for RF library behavior.

### Deliverables
- RF library functioning on CPython3 + sikuligo backend.

### Exit Criteria
- Existing RF example suite runs with minimal/no keyword changes.

## Workstream 7: Test Strategy and CI
### Scope
Build confidence for parity and prevent regressions.

### Tasks
1. Create test layers:
   - unit tests for adapter and transforms
   - integration tests with running `sikuligo`
   - end-to-end sample map tests
2. Update CI matrix:
   - Linux/macOS/Windows where practical
   - install/build `sikuligo` binary before tests
3. Add gating checks:
   - backend smoke test
   - sample workflow test

### Deliverables
- CI passing for migrated path.

### Exit Criteria
- Merge gate verifies adapter-based execution path on every push/PR.

## Workstream 8: Cutover and Cleanup
### Scope
Finalize migration and remove legacy-only code.

### Tasks
1. Default backend to `sikuligo`.
2. Remove deprecated Java/Jython wrappers and imports.
3. Update docs and quickstarts.
4. Archive unsupported legacy behaviors explicitly.

### Deliverables
- Single supported runtime path (CPython3 + sikuligo).

### Exit Criteria
- No mandatory runtime dependency on Java SikuliX modules.

## 6. API Mapping (Legacy -> Sikuligo)
| Legacy concept | Migration target |
| --- | --- |
| `Screen(0)` | `Screen()` (auto connect/spawn) |
| `Pattern(path).similar(x)` | `Pattern(path).similar(x)` |
| `Pattern(path).exact()` | `Pattern(path).exact()` |
| `Region.find(pattern)` | `screen.region(...).find(pattern)` or framework wrapper |
| `Region.exists(pattern, t)` | `exists(..., timeout_millis=...)` |
| `Region.wait(pattern, t)` | `wait(..., timeout_millis=...)` |
| `Region.click(pattern)` | `click(pattern)` |
| `FindFailed` | mapped `SikuliError`/framework exceptions |

## 7. Identified Gaps and Required API Decisions
- Confirm/extend drag-and-drop parity in `sikuligo` for entity drag behaviors.
- Confirm keyboard modifier support needed by text entity classes.
- Confirm capture API for logging artifacts in formatter.
- Confirm region geometry utility parity (above/below/left/right/nearby) in adapter.

## 8. Risk Register and Mitigations
1. **Behavior drift in image matching**
   - Mitigation: parity tests with golden baselines and score thresholds.
2. **Robot Framework regressions**
   - Mitigation: keyword-level integration tests before backend default switch.
3. **Unsupported advanced input semantics**
   - Mitigation: explicit feature matrix and staged server/client API additions.
4. **Cross-platform stability issues**
   - Mitigation: CI matrix + per-OS adapter guards.

## 9. Suggested Sequence and Milestones
1. M1 (Week 1): Workstreams 0-1 complete.
2. M2 (Week 2): Workstream 2 complete (adapter + smoke tests).
3. M3 (Week 3): Workstreams 3-4 complete (finder/entity core).
4. M4 (Week 4): Workstreams 5-7 complete (logging/RF/CI).
5. M5 (Week 5): Workstream 8 cutover and cleanup.

## 10. Definition of Done
- Framework runs on CPython 3 with `sikuligo` as primary backend.
- Core examples pass using real UI automation flow.
- Robot Framework path validated.
- CI enforces migrated path and no legacy Java import reliance.
- Documentation updated with new setup and quickstart.
