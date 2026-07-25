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

Given the user opens SCREEN-001  
When the user selects and saves a supported value  
Then the value is restored after the application restarts.

