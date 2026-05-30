# 쿠라's 노래책 — CURRENT_TASK

## Current Goal

쿠라's 노래책 Google Sheets MVP를 GitHub Pages 기반 정적 웹사이트로 이전하기 위한 초기 skeleton을 만든다.

## Current Phase

Phase 0 — Project setup and Codex onboarding.

## Source of Truth

Read these first:

1. `docs/00_PROJECT_STATE_v1_0.md`
2. `docs/01_WEB_MIGRATION_SPEC.md`
3. `docs/02_DESIGN_BRIEF.md`
4. `docs/03_CURRENT_TASK.md`

Use `source_archive/` only as historical reference.

If `docs/` conflicts with `source_archive/`, follow `docs/`.

## Important Rules

- Do not edit files before summarizing your understanding.
- Do not implement backend.
- Do not add login/account features.
- Do not use Supabase/Firebase.
- Do not implement Google Sheets auto sync.
- Do not infer schema from xlsx directly.
- Do not replicate Google Sheets formulas 1:1.
- Default to plain HTML/CSS/JS.
- Do not introduce React/Vite/build tools unless you explain the trade-off and get approval.
- Keep mobile usability high.
- Keep the design cute but not childish.
- Avoid SaaS dashboard styling.

## First Codex Prompt

Before editing any files, inspect this repository and summarize:

1. What this project is.
2. What files and folders currently exist.
3. What source documents you found.
4. The intended data schema.
5. The search/filter behavior.
6. The PC/mobile UI direction.
7. The design direction.
8. The safest first implementation plan.

Then wait for approval.

## First Implementation Target

After approval, implement only the first skeleton:

- `index.html`
- `src/style.css`
- `src/app.js`
- `data/songs.json` sample
- load songs.json
- render sample song cards
- basic search input
- no advanced styling yet

## Next After Skeleton

After the skeleton works:

1. Implement full search logic.
2. Add filters.
3. Add random recommendation.
4. Add video/lyrics buttons.
5. Add responsive mobile card layout.
6. Polish design.
7. Add xlsx/csv to JSON conversion workflow.
