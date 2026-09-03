# FLOW-001 — Change preference

Linked requirements: REQ-001  
Linked screens: SCREEN-001

## Goal

Persist a valid user preference.

## Entry and exit conditions

Enter from settings. Exit after the saved value is visible.

## Ordered steps

1. Open the preference screen.
2. Choose a supported value.
3. Save and show the selected value.

## Branches and resume

On failure, keep the previous value and offer retry. After interruption, reload the persisted value.

## AC-001

Given no explicit preference selection has been persisted
When the user saves a supported value on SCREEN-001
Then that value becomes the persisted preference selection.

## AC-002

Given a preference selection was persisted previously
When the user opens SCREEN-001 after the application restarts
Then the persisted value is shown as the current selection.

## AC-003

Given a preference selection is already persisted
When the user saves a different supported value on SCREEN-001
Then the new value replaces the previous persisted selection.
