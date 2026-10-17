# Provenance

## Part C menu implementation - 2026-10-12

- Student(s): Jean Zachary Reyes.
- Artifact: `app/schema/menu_schema.py`, `app/api/routers/menu_routers.py`, `app/services/menu_service.py`, `app/repository/menu_repo.py`, `data/menu_items.json`, `tests/test_menus.py`, and menu documentation.
- Label: **AI-GENERATED**.
- AI tool: OpenAI Codex.
- Purpose: Implement menu viewing, item management, category filtering, and persistence.
- Influence: Used and adapted Codex-generated models, routes, services, repositories, seed data, tests, and documentation.
- Validation: Automated tests described below. Student explanation and teammate review are not established by the automated results.
- PR: [#30](https://github.com/reyeszaki/cosc310-bzs/pull/30).

Inputs: live GitHub issue descriptions for #18, #19, and #20 (read on 2026-10-12, with no separate acceptance-criteria lists); the team's existing FastAPI restaurant foundation; the supplied User stories PDF (US-05, US-06, US-18, and the menu portion of US-20); and the supplied M1 work split.

Codex generated the menu Pydantic models, router, service, JSON repository, fictional demo items, isolated tests, API handoff documentation, and proposed Decision Receipt, with local pytest verification. No external code snippets or additional libraries were introduced. The existing `.gitignore` change predates this work.

 Used Codex to help implement my Part C menu functionality. I still need to review the code, make sure I can explain it during the demo, and get a teammate to review it before merging. I have not recorded teammate approval or contribution percentages here.


## Part C review and refinement - 2026-10-12

- Student(s): Jean Zachary Reyes.
- Artifact: Menu models/routes, `tests/test_menus.py`, and menu API documentation.
- Label: **AI-GENERATED**.
- AI tool: OpenAI Codex.
- Purpose: Refine the generated menu implementation and add validation/persistence regression coverage.
- Influence: Incorporated generated implementation refinements, tests, comments, and documentation. The underlying implementation was already AI-generated.
- Validation: 37 local pytest tests and `git diff --check` passed, as recorded below; no human approval is claimed.
- PR: [#30](https://github.com/reyeszaki/cosc310-bzs/pull/30).

Asked Codex to review the existing project structure and the earlier menu implementation before making changes. With Codex's help, I improved the API documentation for parameters, fields, and 404 responses; added comments explaining price validation, partial updates, test dependencies, and safe file writes; corrected the issue mapping; and expanded the tests. The added tests check that changes persist in a separate Python process, stored data stays intact if a file replacement fails, required fields are validated, and the API documentation matches the implementation.

Verification: `.venv/bin/python -m pytest -q` passed with 37 tests. The installed Starlette/httpx TestClient emits one existing deprecation warning. `git diff --check` passed. No dependencies were added; no commits, pushes, merges, issue edits, or teammate messages were performed. GitHub Actions and a manual frontend/server demo were not run.


## Part C documentation cleanup - 2026-10-14

- Student(s): Jean Zachary Reyes.
- Artifact: `docs/menu-api.md`, README menu overview, and removal of the unapproved menu-storage Decision Receipt.
- Label: **AI-GENERATED**.
- AI tool: OpenAI Codex.
- Purpose: Simplify the earlier AI-generated handoff documentation.
- Influence: Used Codex's rewritten API contract and demo steps; no code or tests changed in this cleanup.
- Validation: 37 pytest tests and `git diff --check` passed, as recorded below.
- PR: [#30](https://github.com/reyeszaki/cosc310-bzs/pull/30) contains the menu work; the exact documentation-cleanup commit is not recorded here.

Asked Codex to simplify the supporting documentation while keeping the menu functionality and tests. Codex shortened `menu-api.md` to the API contract and demo steps, kept the README endpoint overview, and removed the separate, unapproved menu-storage Decision Receipt. The team still needs to select and record its M1 engineering decision. The existing menu progress note was preserved because this checkout has no shared scrum/progress template beyond the team agreement; it can be moved into the team's shared log when available.

No application code or tests were changed. The lock and atomic file replacement were kept to protect against overlapping requests within one process and failed writes. Verification: `.venv/bin/python -m pytest -q` passed with 37 tests; `git diff --check` passed. No dependencies were added, and no commits, pushes, or merges were performed during this cleanup.

## M1 integration review — 2026-10-16

- Student(s): Jean Zachary Reyes.
- Artifact: `app/main.py`, `app/api/restaurant_routes.py`, `app/api/routers/restaurant_routers.py`, `app/schema/restaurant_schema.py`, `app/repository/restaurant_repo.py`, `app/services/restaurant_service.py`, `app/services/menu_service.py`, `static/app.js`, `static/index.html`, `tests/test_m1_integration.py`, `tests/frontend.test.cjs`, `.github/workflows/pytest.yml`, `requirements.txt`, `README.md`, `docs/restaurant-api.md`, `docs/m1-integration-review.md`, and this provenance file.
- Label: **AI-GENERATED**.
- AI tool: OpenAI Codex.
- Purpose: Verify the connected restaurant/menu flow, fix integration defects, add regression tests, and prepare M1 documentation.
- Influence: Incorporated substantial Codex-generated code changes, tests, CI configuration, documentation, and provenance entries. This label records generated content used in the result; it does not imply the student independently wrote those changes.
- Validation: Codex ran 70 Python tests, 5 Node tests, syntax/dependency/diff checks, and a real Chrome UI check against temporary storage. Browser writes survived a server process restart. [GitHub Actions run 29](https://github.com/reyeszaki/cosc310-bzs/actions/runs/38991463232) passed the Python and frontend test steps for commit `a40ecfb904a4397df5e69961e47f7eff8632d6cc`. Student understanding and teammate review must be confirmed separately.
- PR: [#37](https://github.com/reyeszaki/cosc310-bzs/pull/37); initial implementation commit `a40ecfb904a4397df5e69961e47f7eff8632d6cc`.

Codex reviewed the newly integrated frontend, restaurant/menu backend, storage, tests, documentation, and Actions configuration. It fixed visible error handling, apostrophe-sensitive menu editing, literal rendering of user text, restaurant/menu deletion ownership, restaurant write safety/validation, static path resolution, duplicate-router drift, and OpenAPI omissions. It added isolated API/restart/concurrency regression tests and dependency-free frontend regressions, aligned CI runtimes, normalized requirements encoding without changing versions, and completed the M1 README and review report.

Verification: 70 Python tests and 5 Node tests passed; a local headless Chrome check exercised the actual UI against disposable data, including errors, and browser writes persisted through a full server restart. The baseline GitHub Actions run and PR #37 run 29 were confirmed successful, including the updated frontend test step. The existing TestClient warning remains. The review initially made no commits or pushes. At the student's later request, the changes were committed and pushed for PR #37; it remains unmerged. Seed data and the earlier stash were preserved. See `docs/m1-integration-review.md` for exact scope, evidence, and limitations.


## Team verification before submission

The named entries above cover the menu/integration work documented in this chat and its existing history. Each team member must confirm and add entries for any other AI-influenced project artifacts, using the course labels and required fields. No claim is made here about other members' AI use, student explanation, contribution percentages, or teammate approval. These must reflect the team's actual work and agreement.
