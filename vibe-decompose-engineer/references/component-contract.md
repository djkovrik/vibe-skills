# Component contract

Decompose components are UI-independent and lifecycle-aware. Define:

- a public component interface;
- UI-oriented immutable `Model` exposed as `Value<Model>` when state exists;
- callbacks for user actions;
- typed outputs for parent communication;
- a default implementation delegating `ComponentContext`;
- a static preview implementation for every contract rendered by production Compose.

Keep UI dependent on the component and keep Compose/platform types out of the contract.

## Component-module layout

Use this package shape inside each screen/flow component module:

```text
<feature>/
  FeatureComponent.kt
  domain/                 # only when feature-local managers/models exist
  integration/
    FeatureComponentDefault.kt
    FeatureComponentPreview.kt
    Mappers.kt            # when Store State maps to Component.Model
  store/                  # only for Store-backed components
    FeatureStore.kt
    FeatureStoreProvider.kt
```

The contract stays at the feature package root. Production/preview implementations, Stores, and feature-domain helpers belong to distinct subpackages even when the feature is small. Additional cohesive subpackages are allowed, but flattening `Component`, `Default`, Store, and Manager files into one package is not.

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

Place `*ComponentPreview` beside `*ComponentDefault` in the component module's `integration` package for every public component contract rendered by production Compose. This includes stateless callback-only screens. It implements the same public interface, may use a static `MutableValue(Model(...))`, and has no Store, `ComponentContext`, Manager, repository, platform service, or production wiring. Compose previews must instantiate this implementation instead of declaring private ad-hoc component fakes in the Compose module. Never insert preview implementations into production child factories.

A navigation/composition-only component with no production Compose render surface may omit a Preview implementation. Record the exception; do not infer it merely because the component has no `Value<Model>`.

Official sources:

- https://arkivanov.github.io/Decompose/
- https://arkivanov.github.io/Decompose/component/overview/
- https://arkivanov.github.io/MVIKotlin/binding_and_lifecycle/
