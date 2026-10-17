# AI Use and Provenance

## M0 foundation

- **Student(s):** Jean Zachary Reyes
- **Artifact:** My contributions to the M0 backend foundation and project setup, identified by the `foundation-gate` tag.
- **Label:** AI-ASSISTED
- **AI tool:** Not recorded for M0.
- **Purpose:** Get guidance while completing my M0 work.
- **Influence:** I wrote the final work myself and used AI for ideas or guidance. This entry records my AI use, not the other team members' work.
- **Validation:** M0 included pytest checks for health, restaurant listing, isolated JSON repository reads, and an invalid endpoint. Historical test-run results are not recorded in this entry.
- **Version:** [`foundation-gate`](https://github.com/reyeszaki/cosc310-bzs/tree/foundation-gate)

## M1 menu implementation

- **Student(s):** Jean Zachary Reyes
- **Artifact:** Menu schemas, routes, service, repository, demo menu data, tests, and API documentation in PR #30.
- **Label:** AI-GENERATED
- **AI tool:** OpenAI Codex
- **Purpose:** Help build menu viewing, category filtering, and menu item management.
- **Influence:** I used generated code, tests, and documentation for menu viewing/filtering, item management, validation, and JSON persistence.
- **Validation:** The menu work passed 37 tests after its follow-up checks, including separate-process persistence and failed-write protection.
- **PR:** [#30](https://github.com/reyeszaki/cosc310-bzs/pull/30)

## M1 documentation

- **Student(s):** Jean Zachary Reyes
- **Artifact:** `README.md` and `docs/PROVENANCE.md` in PR #37.
- **Label:** AI-GENERATED
- **AI tool:** OpenAI Codex
- **Purpose:** Finish the M1 setup, API, testing, and submission documentation.
- **Influence:** I used AI-generated documentation and then asked for shorter wording. The application code, additional tests, and CI changes initially proposed in this PR were reverted because they changed other members' parts. Only the README and this provenance update remain in the PR.
- **Validation:** The documentation was checked against the restored routes, frontend, tests, and workflow. The original suite has 49 tests. Earlier 70-test and browser results were for the removed implementation and do not establish that the restored code passes those checks.
- **PR:** [#37](https://github.com/reyeszaki/cosc310-bzs/pull/37)

## Part B create, update, delete restaurant - 2026-10-15

- **Student(s):** Keyan Sharifpour
- **Artifact:** Restaurant GET/POST/PUT/DELETE handling in `app/api/routers/restaurant_routers.py`, `app/services/restaurant_service.py`, `app/repository/restaurant_repo.py`, `app/schema/restaurant_schema.py`, and tests in `tests/test_restaraunts.py`.
- **Label:** AI-GENERATED
- **AI tool:** OpenAI Codex and PyCharm code-completion suggestions.
- **Purpose:** Implement returning, creating, updating, and deleting restaurant data, with tests for successful and invalid requests.
- **Influence:** I used generated code and code-completion suggestions for the functions and tests. The implementation follows user → route → service → repository → JSON storage.
- **Validation:** I reviewed the code, tested the FastAPI endpoints locally, and ran pytest checks for successful requests and invalid input. All tests passed on my local machine.
- **PRs:** [#32](https://github.com/reyeszaki/cosc310-bzs/pull/32), [#40](https://github.com/reyeszaki/cosc310-bzs/pull/40).

## M1 frontend and API documentation

- **Student(s):** Shawn Goh
- **Artifact:** static/index.html, static/app.js, app/main.py, .github/workflows/pytest.yml, and docs/restaurant-api.md
- **Label:** AI-GENERATED
- **AI tool:** Google Gemini
- **Purpose:** Build frontend user portal, configure static file mounting, set up the GitHub Actions CI workflow, and write the restaurant API documentation.
- **Influence:** Used and adapted the generated HTML/JS client code, CI configuration YAML, FastAPI static file mounting, and API documentation.
- **Validation:** Tested the web server locally using Uvicorn, verified frontend-to-backend API communication across all routes, confirmed local pytest suite execution, and verified green CI builds on GitHub Actions. All code is read and reviewed before use.
- **PR:** #34

## Team contributions

Each member should record their own AI use. Work written by a student using AI only for ideas or guidance belongs under AI-ASSISTED; generated code or text used in the project belongs under AI-GENERATED. Teammate review and understanding of the submitted work still need to be confirmed by the team.
