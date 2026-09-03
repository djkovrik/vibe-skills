# FLOW-001 — Save value

Linked requirements: REQ-001  
Linked screens: SCREEN-001

## Goal

Persist and expose a value.

## Entry and exit conditions

Enter with no value. Exit after the value is visible.

## Ordered steps

1. Open SCREEN-001.
2. Save the value.

## Branches and resume

Retry after a failure.

## AC-001 — Saved value is observable

Given the fixture is open.

When the user saves a value.

Then the public component model exposes that value.
