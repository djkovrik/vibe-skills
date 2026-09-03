# FLOW-001 — Manage meals

Linked requirements: REQ-001  
Linked screens: SCREEN-001

## AC-001

Given a saved preset exists  
When the user renames it  
Then the new preset name is visible after reload.

## AC-002

Given a saved preset exists  
When the user updates its contents  
Then the changed contents are visible after reload.

## AC-003

Given a history entry exists  
When the user reuses it  
Then its values initialize the active flow.

## AC-004

Given a history entry exists  
When the user deletes it  
Then it is absent after reload.

## AC-005

Given an interrupted draft exists  
When the user resumes it  
Then its persisted contents are visible in the active flow.

## AC-006

Given a draft exists  
When the user discards it  
Then the draft is absent after reload.

## AC-007

Given a draft item exists  
When the user changes its quantity directly  
Then the new quantity is visible after reload.

## AC-008

Given a draft item exists  
When the user removes it directly  
Then that item is absent after reload.

## AC-009

Given several selected draft items exist  
When the user deletes one selected item  
Then only that item is absent after reload.
