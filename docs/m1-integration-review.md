# M1 integration review — 2026-10-16

Reviewed checkout: main at `5149f96959e2f64b4fca35ea5997c6803cd7e610`, followed by the local fixes below. Earlier review changes remain in the existing stash; they were not reapplied.

## Connected flow

The served frontend at `/` calls the registered restaurant router for list/search, details, POST creation, PUT updates, status changes, and deletion. It calls the menu router for menu/category GETs, item POST/PATCH/DELETE operations, and availability updates. Requests use the same origin. Every API operation passes through a service and repository to JSON; frontend lists are populated from HTTP responses, not hard-coded records. The fictional demo data lives in `data/`.

Restaurant and item IDs are integers. Items carry `restaurant_id`; menus are derived from those items rather than separate menu records. Restaurant PUT sends all four required editable fields; item PATCH preserves omitted fields. Price responses are JSON numbers. The frontend displays two decimal places. Existing category matching handles case/whitespace, empty categories, empty menus, and unavailable items correctly.

## Issues fixed

- Several frontend mutations lacked catches or ignored unsuccessful responses. A shared request helper now checks statuses and exposes backend, validation, non-JSON server, and network errors. Failed detail loading clears the previous selection instead of leaving forms pointed at an old restaurant.
- An apostrophe inside encoded item JSON broke the inline Edit Item handler. Apostrophes are now encoded explicitly, and user-provided restaurant/item text is escaped before HTML rendering.
- A restaurant could be deleted while its menu items remained. Because IDs can be reused, those items could become another restaurant's menu. Deletion now returns 409 until items are removed. Menu creation and restaurant deletion share the restaurant lock to preserve ownership during overlapping requests in one worker.
- Restaurant writes could truncate existing JSON on a failed write or lose overlapping updates. They now use atomic replacement and a shared thread lock, following the existing menu repository approach. The repository update annotation now matches the dictionary passed by the service.
- Restaurant validation accepted whitespace-only text and silently ignored unknown fields; this contradicted the API handoff. Text is trimmed, extra fields are rejected, and path IDs must be positive. The existing full-body PUT contract was preserved.
- OpenAPI omitted restaurant 404 responses. Added those responses and the deletion 409 behavior. Corrected the inconsistent update error text.
- Static hosting used a working-directory-relative path and failed when imported from another directory. It now resolves from source. An older unregistered restaurant router is now a compatibility import of the real router, avoiding two competing implementations.
- README still described M0 and claimed the frontend was future work. Replaced it with M1 setup, API/storage contracts, verification, scope, limits, and a complete UI walkthrough. Updated the restaurant handoff too.
- CI used Python 3.10 while the README required 3.14. Aligned it to 3.14 and added Node 22/frontend regression tests. Converted requirements from UTF-16 to UTF-8/LF without changing package pins.

## Executed verification

- Baseline: **49 pytest tests passed** before changes.
- Final: **70 pytest tests passed** on Python 3.14.0. This includes a real Uvicorn HTTP server using temporary JSON, then stopping and starting a new process to verify restaurant and menu create/update persistence.
- **5 dependency-free Node frontend regression tests passed**, covering apostrophe edit handlers, literal rendering, API/network/non-JSON errors, and failed-details selection reset. These simulate DOM elements; they are not browser tests.
- A separate **headless Chrome/Playwright run passed** against a disposable server/data directory: create/search/filter, details, restaurant update, menu creation/editing with `Chef's Tea`, price/availability, category filtering and empty results, 409 deletion message, injected 422 validation response, and a simulated network failure. No page errors occurred. After stopping/restarting the server, an HTTP read confirmed those actual browser writes persisted. This was a local exploratory check, not an installed CI browser suite.
- Existing and new tests cover missing IDs, cross-restaurant access, invalid/no-op writes, atomic replacement failure preservation, overlapping restaurant creates, concurrent menu-add/restaurant-delete ownership, menu deletion persistence, default-data schema/relationship consistency, and serving static files outside the project working directory.
- JavaScript syntax check, `python -m pip check`, and `git diff --check` passed. Committed data files remained unchanged.
- GitHub's [main baseline run](https://github.com/reyeszaki/cosc310-bzs/actions/runs/38990208335) completed successfully; its `Run test suite` job step was confirmed successful through the GitHub API. The new local workflow changes have not run remotely because nothing was pushed.

An intermediate regression check failed because restaurant OpenAPI did not document 404; that was fixed and the full suite passed. Initial socket binding in the earlier review required permission outside the sandbox. Current HTTP/browser checks were run with permission. One existing Starlette/httpx TestClient deprecation warning remains; it does not fail tests.

## Inspected only and remaining limits

A clean dependency installation, other browsers, and the modified workflow on GitHub were not executed. CI runs pytest and Node DOM regression tests; it does not run Chrome. This review verifies the requested restaurant/menu slice, not unspecified M1 requirements outside that slice.

Use one API worker. JSON locks do not coordinate multiple processes, and there is no cross-file transaction/database. The restaurant file must exist; menus initialize on first add. IDs may be reused after deletion and are not ready as permanent order references. Storage errors return server errors that the UI now displays. Authentication/authorization, carts, orders, and payments are outside this slice.

No commits, pushes, merges, demo-data mutations, or stash changes were performed. See the README's manual walkthrough for repeatable browser verification, including error cases and a restart.
