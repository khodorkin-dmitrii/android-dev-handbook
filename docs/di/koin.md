# Koin

Koin is a Kotlin-first dependency injection framework commonly used in Android projects. It describes modules and dependencies with a Kotlin DSL instead of the same annotation-heavy setup used by Dagger/Hilt.

Koin is a good fit for smaller and medium Android apps, prototypes, pet projects and teams that prefer simple configuration. It is also relevant for Kotlin Multiplatform-oriented architecture, although Android remains the main focus here.

## Koin basics

```kotlin
val appModule = module {
    single { ApiService(get()) }
    single { UserRepository(get()) }
    viewModel { UserViewModel(get()) }
}
```

`module {}` groups dependency definitions. `single {}` creates an application-level singleton. `factory {}` creates a new instance each time. `viewModel {}` integrates with Android `ViewModel` creation. `get()` resolves another dependency from the Koin container.

Koin is usually started from the `Application` class:

```kotlin
startKoin {
    modules(appModule)
}
```

## Koin vs Hilt

| Topic | Hilt | Koin |
| --- | --- | --- |
| Configuration style | Annotations and generated Dagger code | Kotlin DSL modules |
| Compile-time vs runtime behavior | Compile-time graph generation and validation | Runtime dependency resolution |
| Boilerplate | More setup concepts, less manual Dagger wiring | Usually less setup and very readable modules |
| Android integration | Strong standard integration with Android lifecycle components | Android integrations for `ViewModel`, scopes and common app setup |
| Error detection | Many graph problems fail during build | Misconfigured modules are more likely to fail at runtime |
| Refactoring safety | Stronger because generated code and compile-time checks catch many mistakes | Good readability, but more discipline and tests are needed |
| Learning curve | More concepts: components, scopes, modules, qualifiers | Easier to start if the team knows Kotlin |
| Best fit | Large, complex, long-lived production Android apps | Small and medium apps, prototypes and KMP-friendly codebases |

Hilt is built on top of Dagger and is usually the default recommendation for large production Android apps because it provides stronger compile-time guarantees. Koin is a valid modern alternative when simplicity, fast setup, Kotlin DSL or Kotlin Multiplatform-friendly architecture matters.

Modern Koin has tools and features that improve module validation, but the core trade-off remains: Koin is simpler and more dynamic, while Hilt is stricter and safer for large dependency graphs.

## Practical recommendation

### When to use Koin

Use Koin when the project is small or medium-sized, the team wants DI without heavy annotation processing or code generation setup, or the codebase is oriented toward Kotlin Multiplatform.

Koin also works well for pet projects, prototypes and apps where runtime DI trade-offs are acceptable and readable Kotlin configuration is more valuable than strict compile-time graph validation.

### When Hilt is usually better

Hilt is usually better for large production Android apps with complex dependency graphs, many modules and many developers.

Choose Hilt when strong compile-time validation is important or the team already follows the Google-recommended Android architecture stack.
