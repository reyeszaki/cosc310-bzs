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

**Student(s):** Keyan Sharifpour

Implemented the handling for creating, updating, deleting and returning restaurant
data implementing the GET, POST, PUT, and DELETE requests into functions to process new
and existing data, following through the data flow,
user --> route --> service --> repository --> JSON storage.
Several pytest tests were made to check for errors and success,
based on the data being inputted to fetch and create a restaurant.
Code for the functions and the tests were generated and assisted using both PyCharms code-completion suggestion
aswell as Codex.
All code has been reviewed and tested via FastPointAPI endpoint and all tests have passed
being tested on the local machine

## Team contributions

Each member should record their own AI use. Work written by a student using AI only for ideas or guidance belongs under AI-ASSISTED; generated code or text used in the project belongs under AI-GENERATED. Teammate review and understanding of the submitted work still need to be confirmed by the team.
