# Quality

## Non-functional requirements

Keep local operations responsive.

## Test matrix

Cover AC-001 through the public component contract.

## Repository tests

Run the fixture tests without failures.

## Android release

Produce an Android release build when external release work is being closed.

## Preview and golden matrix

Cover SCREEN-001 in light and dark, EN 100%, and RU 200%.

## Visual quality and design review

Verify approved goldens and complete the post-golden Lazyweb review.

## Accessibility and localization

Support screen readers and system locale selection.

## Localization resource checks

Require equal EN and RU key coverage and reject hardcoded production text.

## Architecture checks

Verify the public component, retained Store, Manager, and preview boundaries.

## Security and privacy

Do not log the value.

## Release acceptance

Require the repository and Android gates.
