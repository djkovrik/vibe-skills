# Navigation and root

- Maintain a strict parent-child `ComponentContext` hierarchy.
- Create the root on the main/UI thread outside Compose.
- Keep configs immutable, serializable arguments; inject services in child factories.
- Own navigation in the nearest parent and route child outputs upward.
- Create navigation/child properties once, not through computed getters.
- Choose `ChildStack`, `ChildSlot`, `ChildPages`, `ChildPanels`, or `ChildItems` by the product relationship.
- Use operations resilient to duplicate clicks and test duplicate-config behavior.

Official sources:

- https://arkivanov.github.io/Decompose/navigation/overview/
- https://arkivanov.github.io/Decompose/extensions/overview/
- https://arkivanov.github.io/Decompose/faq/

