# Component contract

Decompose components are UI-independent and lifecycle-aware. Define:

- a public component interface;
- UI-oriented immutable `Model` exposed as `Value<Model>` when state exists;
- callbacks for user actions;
- typed outputs for parent communication;
- a default implementation delegating `ComponentContext`;
- a static preview implementation when Compose previews need one.

Keep UI dependent on the component and keep Compose/platform types out of the contract.

Official sources:

- https://arkivanov.github.io/Decompose/
- https://arkivanov.github.io/Decompose/component/overview/

