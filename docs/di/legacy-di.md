# Legacy DI

Older Android projects may combine Dagger or Toothpick with MVP, Moxy, and RxJava. Dependency injection (DI) controls how objects are created and connected; Moxy is a presentation framework, not a DI container. When maintaining such a project, trace both the dependency graph and the screen lifecycle before changing either.

## Dagger and Toothpick

Dagger generates binding code and validates the dependency graph at compile time. Missing bindings and many graph errors fail the build. Toothpick resolves dependencies through runtime scopes, so some configuration mistakes appear only when an affected path runs. Neither choice alone guarantees correct scope lifetimes or prevents leaks.

In a legacy feature, identify:

- the composition root and the code that opens and closes each scope;
- which objects are shared across screens, retained across configuration changes, or tied to a single view;
- where runtime parameters enter the graph and how missing bindings are tested.

Do not replace Toothpick with Hilt mechanically. First document object ownership and scope boundaries, then migrate one feature at a time. Test creation, screen recreation, navigation away, and logout where relevant. A scope that outlives its intended owner can retain a presenter, view, or user-specific state even when the DI graph resolves successfully.

For the current Dagger-based approach, see [Dagger / Hilt](dagger-hilt.md) and [DI Basics](basics.md).

## Moxy and the presentation lifecycle

Moxy implements MVP with generated view-state and delegate machinery. A presenter can survive a configuration change and reattach to a recreated view, but that does not make its state durable across process death. Check the project's actual delegate setup and state restoration path.

When DI creates a presenter, inspect who owns it, when the view attaches and detaches, and who disposes of RxJava subscriptions or cancels asynchronous work. A late callback or an incorrectly retained view reference can update a destroyed screen or leak its `Activity` / `Fragment`. Also check that a retained presenter does not hold a short-lived view dependency injected through a longer-lived scope.

For migration, stabilize the existing UI behavior with focused tests, extract reusable data and domain code, then move one screen to `ViewModel` and explicit `UiState` if that fits the feature. Decide separately which state must survive configuration changes and which must survive process death; `ViewModel` alone does not provide durable persistence. See [Legacy & Refactoring](../architecture/legacy-refactoring.md) and [RxJava](../legacy/rxjava.md).
