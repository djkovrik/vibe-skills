# FLOW-001 — Manage preference

Linked requirements: REQ-001  
Linked screens: SCREEN-001

## AC-001

Given no preference exists  
When the user creates a preference  
Then it is visible through the public component contract.

## AC-002

Given a preference exists  
When the user reads the preference  
Then its current value is visible through the public component contract.

## AC-003

Given a preference exists  
When the user updates its value  
Then the changed value is visible after reload.

## AC-004

Given a preference exists  
When the user deletes it  
Then a later read reports no preference.
