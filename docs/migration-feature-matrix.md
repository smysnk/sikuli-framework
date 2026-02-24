# Migration Feature Matrix (Legacy vs SikuliGO Backend)

This matrix tracks behavioral parity during migration from Jython/SikuliX to CPython3 + `sikuligo`.

| Capability | Legacy (Jython/SikuliX) | SikuliGO Backend | Status | Notes |
| --- | --- | --- | --- | --- |
| Runtime | Python 2 + Jython + Java SikuliX | Python 3 + `sikuligo` | In Progress | Migration target runtime is Python 3.10+ |
| Screen bootstrap | `Screen(0)` | `Screen()` | Planned | `Screen()` supports connect-or-spawn behavior |
| Pattern similarity | `Pattern(path).similar(x)` | `Pattern(path).similar(x)` | Planned | API shape is compatible |
| Pattern exact | `Pattern(path).similar(1.0)` / exact semantics | `Pattern(path).exact()` | Planned | Exact maps to similarity 1.0 |
| Find on screen | `Region.find(pattern)` | `find_on_screen` via adapter | In Progress | Adapter implementation started |
| Exists on screen | `Region.exists(pattern, timeout)` | `exists_on_screen` via adapter | In Progress | Timeout mapping required |
| Wait on screen | `Region.wait(pattern, timeout)` | `wait_on_screen` via adapter | In Progress | Interval/timeout parity required |
| Click on screen | Region + input events | `click_on_screen` / input RPCs | In Progress | Left/right/double click mapping pending |
| Hover/mouse move | `mouseMove` | `move_mouse` RPC | Planned | Requires adapter helper |
| Keyboard text input | `type`, Java key modifiers | `type_text`/input RPC path | Planned | Modifier parity to be defined |
| Drag and drop | direct mouse down/up + move | input RPC composition | Planned | Confirm backend support |
| Region transforms (left/right/nearby/etc.) | native Region ops | adapter Region geometry | Planned | Keep existing transform semantics |
| Baseline naming strategy | existing `Finder` logic | unchanged naming + new matcher | Planned | Preserve image lookup contract |
| Logging screenshots | SikuliX capture | backend-compatible capture | Planned | Needed for formatter/report links |
| Robot Framework keywords | existing keyword libraries | same keyword surface | Planned | Internal implementation to switch backend |
| Error model | `FindFailed` and custom exceptions | map `SikuliError` -> framework errors | In Progress | Central mapping needed in adapter |
| Session/interaction tracking | n/a in framework layer | provided by SikuliGO API | Planned | Automatically recorded by API server |

## Gap Priorities

1. Runtime compatibility in core modules (`src/*`) under Python 3.
2. Adapter primitives (`Screen`, `Region`, `Pattern`, `Match`) and error mapping.
3. Finder migration to adapter-backed matching while preserving baseline resolution behavior.
4. Robot Framework keyword compatibility tests.
