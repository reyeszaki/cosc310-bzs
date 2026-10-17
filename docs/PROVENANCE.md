# AI Use and Provenance

I used OpenAI Codex for the menu implementation and the final M1 integration checks. The entries below describe what I used it for and how the results were checked. AI-GENERATED means I used code, tests, or text produced by Codex, including output that was later edited.

## Menu implementation — October 12

- **Student(s):** Jean Zachary Reyes
- **Artifact:** Menu schemas, routes, service, repository, demo menu data, tests, and API documentation: `app/schema/menu_schema.py`, `app/api/routers/menu_routers.py`, `app/services/menu_service.py`, `app/repository/menu_repo.py`, `data/menu_items.json`, `tests/test_menus.py`, and `docs/menu-api.md`.
- **Label:** AI-GENERATED
- **AI tool:** OpenAI Codex
- **Purpose:** Build menu viewing, category filtering, and menu item management for issues #18, #19, and #20.
- **Influence:** I used the generated implementation, tests, and documentation with the existing restaurant backend. The work followed route → service → repository → JSON.
- **Validation:** Automated tests covered menu viewing, filtering, adding/updating/removing items, validation, and restaurant ownership. The menu work passed 37 tests after the follow-up checks.
- **PR:** [#30](https://github.com/reyeszaki/cosc310-bzs/pull/30)

## Menu follow-up work — October 12–14

- **Student(s):** Jean Zachary Reyes
- **Artifact:** Menu models/routes, `tests/test_menus.py`, `docs/menu-api.md`, and the README menu section.
- **Label:** AI-GENERATED
- **AI tool:** OpenAI Codex
- **Purpose:** Check the menu implementation, improve the API handoff, and simplify the documentation.
- **Influence:** I used generated fixes, comments, and tests for required fields, partial updates, price validation, separate-process persistence, and failed writes. I also used the shorter API documentation and removed the unapproved menu-storage Decision Receipt.
- **Validation:** 37 pytest tests and `git diff --check` passed. The documentation cleanup did not change application code or tests.
- **PR:** [#30](https://github.com/reyeszaki/cosc310-bzs/pull/30) contains the menu work; the exact documentation-cleanup commit was not recorded.

## M1 integration fixes and documentation — October 16

- **Student(s):** Jean Zachary Reyes
- **Artifact:** Restaurant routes/models/repository/service, menu service, static hosting, frontend, integration tests, CI, README, restaurant API documentation, and this file. These are the changes in PR #37.
- **Label:** AI-GENERATED
- **AI tool:** OpenAI Codex
- **Purpose:** Check that the restaurant and menu parts work together and finish the M1 documentation.
- **Influence:** I asked Codex to trace the full flow and fix straightforward integration problems. I used its changes for frontend errors, menu editing with apostrophes, safe text rendering, restaurant/menu ownership, restaurant validation, JSON writes, static paths, tests, and CI. I also used its README and provenance wording.
- **Validation:** Codex ran 70 Python tests and 5 frontend regression tests, plus syntax, dependency, and diff checks. A headless Chrome check exercised the actual frontend with temporary data, including error cases. Restaurant and menu changes survived a full server restart. [GitHub Actions run 30](https://github.com/reyeszaki/cosc310-bzs/actions/runs/38991584461) passed both test suites. These are automated checks; teammate review is separate.
- **PR:** [#37](https://github.com/reyeszaki/cosc310-bzs/pull/37)
- **Implementation commit:** `a40ecfb904a4397df5e69961e47f7eff8632d6cc`

## Before submission

Each team member needs to add or confirm entries for their own AI use. This file covers my menu and integration work; it does not describe the other members' AI use. We still need to confirm teammate review and make sure everyone can explain their own work.
