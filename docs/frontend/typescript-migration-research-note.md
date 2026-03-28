# JSX to TSX Migration Research Note (AutoAudit Frontend)

## Purpose
This note documents the rationale and early evaluation for continuing frontend migration from JSX to TSX.

## Scope
- Frontend only
- Practical impact on current modules: Landing, Auth, Scans, Connections

## Method
1. Reviewed current frontend structure and JS/TS mixed state.
2. Completed a pilot migration on the Landing module.
3. Validated behavior and build output after migration.
4. Compared outcomes against common migration practices from official and industry references.

## JSX vs TSX (quick comparison)
- JSX: JavaScript + React syntax, no compile-time type checking.
- TSX: TypeScript + React syntax, compile-time checks for props, state, and data shapes.

## Benefits (Top 3 for AutoAudit)
1. Better bug prevention before runtime.
   - Type checks catch invalid props, missing fields, and incorrect payload usage.
2. Safer refactoring in a team project.
   - Contract changes surface immediately as compile errors.
3. Clearer maintainability and review quality.
   - Types act as documentation for component/API contracts.

## Risks / Challenges (Top 3)
1. Migration effort can slow delivery if done in large batches.
2. Temporary JS/TS mixed codebase increases complexity.
3. Benefits drop if the team relies heavily on `any`.

## Project Evaluation (Pilot: Landing Module)
Migrated:
- `frontend/src/pages/Landing/LandingPage.tsx`
- `frontend/src/pages/Landing/AboutUs.tsx`
- `frontend/src/pages/Landing/featuresData.ts`
- `frontend/src/pages/Landing/components/*.tsx`

Observed outcomes:
- Stronger prop/data contracts in landing components.
- Safer navigation updates (Home returns to top, About opens from top after route change).
- Frontend build remained successful after changes.

Evidence used:
- Local run in development environment.
- Successful `npm run build`.
- Manual route checks: `/`, `/#features`, `/#benefits`, `/about`, `/contact`.

## Recommendation
Continue migration incrementally (module by module), not as a single rewrite.

Suggested rollout order:
1. Auth + components
2. Scans + Connections
3. API typing improvements for `src/api/client.js` usage

Measurable next-step criteria:
- No new `.jsx` files added in migrated modules.
- Each migration PR includes build output and manual route checks.
- Avoid broad `any` usage in new TS/TSX files.

## Limitation
This evaluation is based on the Landing module pilot. More complex modules (Scans/Connections) may require additional migration effort and validation.

## Common Practice References
- TypeScript official migration guide (supports gradual JS + TS coexistence):
  - https://www.typescriptlang.org/docs/handbook/migrating-from-javascript.html
- React official TypeScript guidance:
  - https://react.dev/learn/typescript
- Airbnb migration-at-scale approach (`ts-migrate`):
  - https://medium.com/airbnb-engineering/ts-migrate-a-tool-for-migrating-to-typescript-at-scale-cd23bfeb5cc
- Airbnb `ts-migrate` tool repository:
  - https://github.com/airbnb/ts-migrate
- Slack engineering write-up on TypeScript adoption:
  - https://slack.engineering/typescript-at-slack/
