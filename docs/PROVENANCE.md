# Provenance

## Part C menu implementation - 2026-10-12

Inputs: live GitHub issue descriptions for #18, #19, and #20 (read on 2026-10-12, with no separate acceptance-criteria lists); the team's existing FastAPI restaurant foundation; the supplied User stories PDF (US-05, US-06, US-18, and the menu portion of US-20); and the supplied M1 work split.

Codex generated the menu Pydantic models, router, service, JSON repository, fictional demo items, isolated tests, API handoff documentation, and proposed Decision Receipt, with local pytest verification. No external code snippets or additional libraries were introduced. The existing `.gitignore` change predates this work.

 Used Codex to help implement my Part C menu functionality. I still need to review the code, make sure I can explain it during the demo, and get a teammate to review it before merging. I have not recorded teammate approval or contribution percentages here.


## Part C review and refinement - 2026-10-12

Asked Codex to review the existing project structure and the earlier menu implementation before making changes. With Codex's help, I improved the API documentation for parameters, fields, and 404 responses; added comments explaining price validation, partial updates, test dependencies, and safe file writes; corrected the issue mapping; and expanded the tests. The added tests check that changes persist in a separate Python process, stored data stays intact if a file replacement fails, required fields are validated, and the API documentation matches the implementation.

Verification: `.venv/bin/python -m pytest -q` passed with 37 tests. The installed Starlette/httpx TestClient emits one existing deprecation warning. `git diff --check` passed. No dependencies were added; no commits, pushes, merges, issue edits, or teammate messages were performed. GitHub Actions and a manual frontend/server demo were not run.


## Part C documentation cleanup - 2026-10-14

Asked Codex to simplify the supporting documentation while keeping the menu functionality and tests. Codex shortened `menu-api.md` to the API contract and demo steps, kept the README endpoint overview, and removed the separate, unapproved menu-storage Decision Receipt. The team still needs to select and record its M1 engineering decision. The existing menu progress note was preserved because this checkout has no shared scrum/progress template beyond the team agreement; it can be moved into the team's shared log when available.

No application code or tests were changed. The lock and atomic file replacement were kept to protect against overlapping requests within one process and failed writes. Verification: `.venv/bin/python -m pytest -q` passed with 37 tests; `git diff --check` passed. No dependencies were added, and no commits, pushes, or merges were performed during this cleanup.

## M1 integration review — 2026-10-16

Codex reviewed the newly integrated frontend, restaurant/menu backend, storage, tests, documentation, and Actions configuration. It fixed visible error handling, apostrophe-sensitive menu editing, literal rendering of user text, restaurant/menu deletion ownership, restaurant write safety/validation, static path resolution, duplicate-router drift, and OpenAPI omissions. It added isolated API/restart/concurrency regression tests and dependency-free frontend regressions, aligned CI runtimes, normalized requirements encoding without changing versions, and completed the M1 README and review report.

Verification: 70 Python tests and 5 Node tests passed; a local headless Chrome check exercised the actual UI against disposable data, including errors, and browser writes persisted through a full server restart. The existing baseline GitHub Actions run was confirmed successful; modified local CI has not run remotely. The existing TestClient warning remains. No commits, pushes, merges, seed-data changes, or stash modifications were performed. See `docs/m1-integration-review.md` for exact scope, evidence, and limitations.
