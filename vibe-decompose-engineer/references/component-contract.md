# Component contract

Decompose components are UI-independent and lifecycle-aware. Define:

- a public component interface;
- UI-oriented immutable `Model` exposed as `Value<Model>` when state exists;
- callbacks for user actions;
- typed outputs for parent communication;
- a default implementation delegating `ComponentContext`;
- a static preview implementation when Compose previews need one.

Keep UI dependent on the component and keep Compose/platform types out of the contract.

## Stateful production contract

When a production component exposes UI-visible `Value<Model>`:

- make `Model` immutable;
- implement the component as `*ComponentDefault` delegating `ComponentContext`;
- retain an internal MVIKotlin Store through `InstanceKeeper`;
- keep Store `State` independent from `Component.Model`;
- expose `store.asValue().map(stateToModel)` through a dedicated mapper;
- route callbacks to Store intents or typed outputs;
- do not call repositories/data sources from the component or mutate a production `MutableValue`.

This rule does not apply to `Value<ChildStack>`, `Value<ChildSlot>`, or other values owned by Decompose routers. A component with callbacks/outputs and no UI-visible model remains thin.

## Preview contract

Place `*ComponentPreview` beside `*ComponentDefault` when Compose previews need data. It implements the same public interface, may use a static `MutableValue(Model(...))`, and has no Store, `ComponentContext`, Manager, repository, platform service, or production wiring. Never insert preview implementations into production child factories.

Official sources:

- https://arkivanov.github.io/Decompose/
- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/MVIKotlin/binding_and_lifecycle/
