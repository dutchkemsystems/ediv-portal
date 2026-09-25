# Diagnostic Spec: TDZ Errors on Staff, Students, E-Registry, Workflows

## Goal
Eliminate all four `Cannot access 'X' before initialization` (Temporal Dead Zone) crashes so `/staff`, `/students`, `/registry` (E-Registry), and `/workflows` render cleanly in a production build.

## Project context (read for Phase 1)

| Item | Value |
|------|--------|
| Framework | React 18 SPA |
| Build tool | Vite 5 (`npm run build` → `vite build`) |
| Test runner | Vitest 1.6 + Testing Library |
| Lint | ESLint 8 (`.eslintrc.cjs`) — **no** `import/no-cycle`, **no** `no-use-before-define` |
| Router | react-router-dom 6; pages lazy-loaded in `src/App.jsx` |
| Entry | `src/main.jsx` → `store` → `App` → `Layout` + lazy page |
| Barrel/index | **None** (`src/index.js` does not exist) |
| Deploy | Custom SPA server `frontend-server/server.js` serves `frontend/dist` |
| Lint/build config change policy | New lint rules allowed (required by VERIFICATION-LAYER); **build config changes require stop-and-ask** |
| `STACK_PLAYBOOKS.md` / `feature-map.yaml` | Not present in repo — will create `feature-map.yaml` if verification layer requires it |

### Import chain (common to all four pages)

```
main.jsx
  → store (Redux Toolkit)
  → App.jsx (lazy page)
    → Layout (nav only; no page imports)
    → page (Staff | Students | Registry | Workflows)
        → ../components/common/{DataTable, StatCard, Loading, ConfirmDialog}
        → ../api/client  (axios instance + interceptors)
        → ../utils/notifications  (react-toastify helpers)
        → @mui/material, react, react-redux, etc.
```

### Files already fully read — **no TDZ found**

- `pages/Staff.jsx` (~960 lines), `pages/Students.jsx` (~937), `pages/Registry.jsx` (~660), `pages/Workflows.jsx` (~498) — module-level `const`/`let` declared before use in the portions inspected; component function bodies only run at render, not module-eval.
- `components/common/Loading.jsx`, `ConfirmDialog.jsx` — presentational.
- `utils/notifications.js`, `utils/offlineAttendance.js` — clean; offline util not imported by these pages.
- `App.jsx`, `main.jsx` — clean; no module-eval side effects that touch page bindings.

### Files only partially read (tails not yet inspected)

- `DataTable.jsx` (to ~68), `StatCard.jsx` (to ~51), `api/client.js` (to ~54, mid 401-refresh logic).

### Other observations

- `Workflows.jsx` has a **duplicate** `@mui/material` import block (~lines 44–52) — not a TDZ cause by itself; cleanup candidate.
- Prior commits `ac38f57` / `5e64103` already claimed TDZ fixes + dist rebuild — bug still reported, so either residual source issue, circular import outside page tops, or **stale/incorrect minified artifacts**.
- Minified identifiers differ per page (`T`, `F`, `p`, `v`) → bindings live **inside each page chunk** (or its unique import subgraph), not a single shared constant.

## Page → module → suspected TDZ source

| Page | Route | Page module | Suspected TDZ source (ranked) |
|------|-------|-------------|-------------------------------|
| Staff | `/staff` | `src/pages/Staff.jsx` | 1) Unread tail of page or `DataTable`/`StatCard`/`client` use-before-declare 2) Circular import in page-unique subgraph 3) Stale minified chunk in `dist` masking fixed source |
| Students | `/students` | `src/pages/Students.jsx` | Same pattern; distinct binding `F` → page-specific (or page-specific dep) binding |
| E-Registry | `/registry` | `src/pages/Registry.jsx` | Same; binding `p`; path in App is `/registry` (nav label “E-Registry”) |
| Workflows | `/workflows` | `src/pages/Workflows.jsx` | Same; binding `v`; duplicate MUI import noted as cleanup only |

### Common causes checklist (directive §1c)

| # | Cause | Status |
|---|--------|--------|
| 1 | Circular imports, module-eval read of other export | **Open** — not fully proven; no cycle found in fully-read files; tails + store/Layout not exhaustively proven |
| 2 | Barrel re-export cycle | **Ruled out** — no barrel/index under `src/` |
| 3 | Top-level function called during module init before `const` init | **Open** — would appear in unread tails |
| 4 | Class field initializer ordering | **Unlikely** — pages are function components |
| 5 | Context/store created before deps | **Open** — `src/store` not fully audited |
| 6 | Enum/const in decorator or module-level before declaration | **Unlikely** — no TS/decorators in these files |
| 7 | Dynamic import order | **Low** — `lazy(() => import(...))` is standard; chunks load on route |

## In Scope

- Root-cause fix for the four listed pages only.
- Finishing unread tails (`DataTable`, `StatCard`, `api/client`, page tails) and `store` audit if cycle suspected.
- Fresh production build so `dist` matches source.
- Regression tests that fail without the fix.
- Proof bundles for the four routes.
- ESLint rules required by VERIFICATION-LAYER: `import/no-cycle` (error), `no-use-before-define` for `variables`/`classes` (error) — **only if** investigation confirms that class of cause; otherwise add the rule that matches the actual root cause and document why.
- `feature-map.yaml` verification timestamps if verification layer creates it.

## Out of Scope

- Architectural refactors beyond the TDZ fix.
- New runtime dependencies.
- Build configuration changes (`vite.config.js`) — stop-and-ask.
- Fixes for pages not in the bug list (except incidental lint-rule noise triage).
- Pushing to a non-current branch; deploying to non-production.

## Success criteria

1. `npm run build` in `frontend/` completes with zero errors.
2. `npm run test` passes, including new regression coverage for the TDZ class of bug.
3. Production build (`npm run start` / served `dist`) loads `/staff`, `/students`, `/registry`, `/workflows` with **zero console errors**.
4. Screenshot + console + network proof bundles at `./proof/<page>/<timestamp>/`.
5. `feature-map.yaml` updated with `verified_at` (created if missing).
6. Lint rules committed with the fix; lint runs clean on the fixed files.
7. @verification-engineer reports green; final approval from @reality-checker before ship.

## Diagnosis open item (must close in Phase 2 plan)

**Exact binding names** (`T`/`F`/`p`/`v`) cannot be mapped without either (a) reading remaining file tails + import graph, or (b) a build with readable names / sourcemaps. Phase 2 will pick (a) first (cheapest); if inconclusive, one diagnostic unminified/`sourcemap: true` build **does not change app behavior** and is used only for stack traces — flagged as optional and shown before any persistent config change.

## Stop gate

Spec written. **No source code changes until this spec is approved.**
