# Design-to-golden loop

1. Validate screen requirement/state coverage.
2. Gather Lazyweb evidence and approve a direction.
3. Define hierarchy, tokens, responsive/accessibility/localization behavior.
4. Implement through the component contract and Compose Expert.
5. Create deterministic previews for approved states.
6. Ask Visual Testing to record.
7. Inspect rendered PNGs/diffs against intent.
8. Verify goldens in CI.

Goldens are evidence of approved rendering, not an authority that overrides AppSpec or accessibility behavior.

