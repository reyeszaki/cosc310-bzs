# Decision Receipt: M1 menu storage

Date: 2026-10-12
Status: Implemented proposal; pending teammate review

## Problem

Part C needs editable menus without mixing restaurant metadata and menu mutations or bypassing the required repository layer.

## Decision

Store menu items in a separate JSON list, linked by integer `restaurant_id`. Validate requests with Pydantic, require positive prices with at most two decimal places, and use Decimal during validation. Serialize prices as JSON numbers for the frontend. Expose view, create, partial update, and removal under each restaurant's menu route.

Repositories own all file operations; services check that restaurants exist; routes translate missing records to HTTP 404. Writes use atomic replacement and an in-process lock.

## Alternatives and tradeoffs

Embedding menus in restaurant records would require C and B to write the same file. A database would give stronger concurrency and ID guarantees but exceeds the current JSON/CSV architecture. Separate JSON keeps integration small, with one-worker operation as a limitation. Category strings allow filtering without introducing a category-management subsystem.

## Evidence

Isolated pytest tests cover customer-visible changes, availability, category filtering, cross-restaurant isolation, rejection of invalid payloads, removal, and a separate Python process to verify persistence. A failed replacement test verifies that the original data remains intact. The team should review the endpoint contract and tradeoffs before treating this as an agreed team decision.
