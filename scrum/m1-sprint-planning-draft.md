# M1 Sprint Planning

## Sprint Information

- **Sprint / Milestone:** Milestone 1 — restaurant and menu flow
- **Sprint dates:** October 9–16, 2026
- **Planning meeting date:** Friday, October 9, 2026
- **Facilitator:** [Confirm]
- **Record status:** Draft based on our confirmed work split and planning date. Attendance, facilitator, and the proposed checkpoints still need confirmation.

### Team Members

Attendance marked by request:

- [x] Beab Girma Yifrashewa
- [x] Jean Zachary Reyes
- [x] Shawn Goh
- [x] Keyan Sharifpour

## 1. Sprint Goal

We want a working restaurant and menu flow that we can run from the browser. A user should be able to find a restaurant, open its details, and view or filter its menu. We also need to create and update restaurants and menu items, with changes staying saved after the app restarts.

## 2. Sprint Backlog

Our work is split into four sections so we can work in parallel and connect the parts before submission.

| User Story | Description | Priority | Primary Owner | Dependencies |
|---|---|---|---|---|
| #11, #29 | Restaurant list, name search, cuisine and open-status filters | High | Beab | Existing restaurant schema and JSON records |
| #16, #38, #39 | Restaurant details and create/update/delete operations | High | Keyan | Existing restaurant repository and stable IDs |
| #18, #19, #20 | Manage menu items, view menus, and filter by category | High | Jean | Restaurant IDs and restaurant existence checks |
| Frontend integration for the stories above | Connect the restaurant and menu pages/forms to the API | High | Shawn | Restaurant and menu endpoint contracts |

Primary ownership means coordinating that section. We can help with testing and reviews without taking over someone else's files.

## 3. Task Decomposition

### Restaurant discovery — Beab

- [x] Return the restaurant list through the route, service, and repository.
- [x] Search by name and filter by cuisine and open/closed status.
- [x] Combine filters and return an empty list when nothing matches.
- [x] Test blank searches, no matches, combined filters, and invalid open-status values.
- [x] Share the query parameters with Shawn for the frontend.

### Restaurant details and management — Keyan

- [x] Return the selected restaurant's details using its ID.
- [x] Create restaurants with name, cuisine, address, and open status.
- [x] Update existing restaurant information and delete by restaurant ID.
- [x] Keep IDs consistent across the API and JSON storage.
- [x] Test successful requests, missing IDs, and invalid input.
- [x] Check that saved changes remain after restarting the app.
- [x] Document request bodies and responses.

### Menus — Jean

- [x] View a menu using its restaurant ID.
- [x] Add, update, and remove menu items.
- [x] Support categories, prices, descriptions, and availability.
- [x] Filter by category and allow the filter to be cleared.
- [x] Test validation, missing items, wrong-restaurant requests, and persistence.
- [x] Share the menu API contract with Shawn.

### Frontend — Shawn

- [x] Load restaurants from the backend and connect the search/filter controls.
- [x] Open the selected restaurant's details and menu.
- [x] Connect restaurant create/update/delete forms to the correct endpoints.
- [x] Connect menu item forms and category filtering.
- [x] Display prices to two decimal places and show unavailable items clearly.
- [x] Show useful messages for empty results and failed requests.
- [x] Walk through the complete flow in the browser with the backend running.

### Shared handoff and submission

- [x] Review each other's PRs and discuss changes affecting another section.
- [x] Run pytest and check GitHub Actions before merging.
- [x] Test the combined flow after the parts are integrated.
- [x] Update the README, API documentation, and individual provenance entries.
- [x] Add our actual scrum records and update the project board.
- [x] Confirm the contribution statement, final tag, and Canvas PDF.

## 4. Dependencies and Integration

| Dependency | Related User Stories | Who is Responsible? | Planned Resolution |
|---|---|---|---|
| Restaurant IDs connect details and menu records | #11, #16, #18, #19 | Keyan and Jean | Use the same integer restaurant IDs and verify menu ownership |
| Frontend needs the final restaurant URLs and payloads | #11, #16, #29, #38, #39 | Beab, Keyan, and Shawn | Share the restaurant API contract and test requests together |
| Frontend needs the menu response and category parameter | #18, #19, #20 | Jean and Shawn | Use the menu API handoff and check the browser against real responses |
| Final testing needs all parts on the same version | All M1 stories | Everyone | Review PRs, integrate approved work, then run the full walkthrough |

### Integration Plan

We will keep our work on separate branches and use PRs to bring it together. Before changing a shared file, we will check with the person handling that section. Backend changes should keep the route → service → repository → JSON flow.

Once the endpoints are available, Shawn can connect the frontend using the documented fields and responses. We will test the complete path from the restaurant list to an updated menu item, then restart the app and check that the changes are still there. Any problems outside our own section should go back to its owner for review.

### Completion Deadlines

**M1 submission deadline:** Friday, October 16, 2026. Check Canvas for the exact cutoff time.

The checkpoints below are proposed dates for the October 9–16 sprint. We still need to confirm which deadlines were agreed to during our discussion.

| Target | Task | Owner |
|---|---|---|
| Tuesday, October 13 | Backend sections and API handoffs ready for integration | Beab, Keyan, Jean |
| Wednesday, October 14 | Frontend connected to the restaurant and menu APIs | Shawn, with backend owners available |
| Thursday, October 15 | Complete the browser walkthrough, restart checks, and PR reviews | Everyone |
| Friday, October 16, before tagging | Finish documentation, provenance, scrum notes, and project-board updates | Everyone; Jean prepares the submission document |
| Friday, October 16, before the Canvas cutoff | Confirm the final tag/SHA and upload the PDF | One team member, to confirm |

## 5. Risks and Potential Blockers

| Risk / Blocker | Impact | Planned Action | Owner |
|---|---|---|---|
| Different field names, IDs, or endpoint assumptions | Frontend requests fail or show the wrong data | Compare requests with the API documentation before integration | Each backend owner and Shawn |
| Multiple people changing shared restaurant files | Merge conflicts or changes to someone else's section | Coordinate changes and have the section owner review the PR | Everyone |
| Tests pass but the full browser flow still fails | Problems are found too late | Run a real browser walkthrough and restart check | Everyone |
| Late fixes leave no time for review or documentation | Incomplete submission | Keep a final review buffer and track remaining tasks on the board | Everyone |

## 6. Definition of Done

Checklist marked complete at Jean's request. The boxes record the requested status; this edit does not add new test or review evidence.

- [x] Requirements and acceptance criteria are satisfied.
- [x] Business logic is in the service layer.
- [x] Persistence goes through the repository layer.
- [x] Appropriate unit and API tests are included and pass.
- [x] The frontend uses the real API for the complete flow.
- [x] Saved changes remain after restarting the app.
- [x] At least one teammate has reviewed the code.
- [x] Review feedback has been addressed.
- [x] Documentation and provenance are updated.
- [x] Approved changes are integrated into the team's working version.
- [x] No known critical defects remain.

## 7. Sprint Commitment

| Team Member | Initial Responsibilities | Confirmed |
|---|---|---|
| Beab | Restaurant list, search, and filters | Work split confirmed; individual commitment to confirm |
| Keyan | Restaurant details and create/update/delete operations | Work split confirmed; individual commitment to confirm |
| Jean | Menus, menu items, and submission document preparation | Work split confirmed; individual commitment to confirm |
| Shawn | Frontend and API integration | Work split confirmed; individual commitment to confirm |

## Meeting Notes

The main handoff is between the backend sections and the frontend. We need to keep the restaurant IDs and request/response fields consistent so the parts connect properly. Each owner should provide tests and enough API documentation for the next person to use their section.

We should review the full application together before calling M1 complete. Passing unit tests is one check, but we also need to try the actual browser flow, verify errors and empty results, and restart the app to check saved changes.

Our planning discussion was on October 9, and M1 is due October 16. Before finalizing these notes, we need to confirm attendance, the facilitator, and whether the proposed checkpoints match our discussion.
