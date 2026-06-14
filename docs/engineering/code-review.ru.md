# Code Review

Code review - это практика качества для проверки корректности, maintainability, shared ownership, knowledge sharing и снижения production risk. Это не поиск виноватого.

Code review применяет многие идеи из [Code Quality](code-quality.md): readability, maintainability, code smells, unnecessary abstractions и safe refactoring.

## Зачем нужен code review?

Code review помогает команде находить проблемы до production и сохранять codebase понятной не одному человеку, а всей команде. Он также распространяет контекст: reviewers узнают изменение, а автор получает feedback до того, как код станет частью общей системы.

Хорошее review проверяет и behavior, и maintainability. Код может работать сегодня, но быть сложным для изменения завтра, если он прячет state, смешивает layers или добавляет premature abstractions.

**Коротко:** code review снижает production risk и сохраняет ownership кода shared внутри команды.

## Что проверять в pull request?

Pull request стоит проверять с нескольких сторон:

- correctness - решает ли изменение нужную задачу;
- readability - сможет ли другой разработчик быстро понять код;
- maintainability - можно ли безопасно менять этот код дальше;
- architecture boundaries - остается ли logic в правильном layer;
- state and lifecycle - безопасно ли состояние owned и collected;
- error handling - явно ли представлены и обработаны failures;
- tests - покрыты ли важные случаи;
- performance - нет ли лишней работы на hot paths;
- security and privacy - безопасно ли обработаны sensitive data и permissions;
- UX states - loading, empty, error и disabled states.

Не каждый PR требует глубокой дискуссии по каждому пункту. Глубина review должна соответствовать риску и размеру изменения.

**Практический совет:** сначала проверяй observable behavior и contracts, потом implementation details.

## Как ревьюить Android-код?

В Android code review важно учитывать platform-specific risks:

- lifecycle safety;
- отсутствие `Activity` / `Context` leaks;
- случайная работа на main thread;
- coroutine scope and cancellation;
- `Flow` collection and lifecycle awareness;
- Compose recomposition and state issues;
- navigation and one-off events;
- resource handling;
- configuration changes;
- error, empty и loading states.

Для `ViewModel` стоит проверить, что UI state явный, а side effects не смешаны с durable state. Для Compose - ownership состояния, stable inputs и unnecessary recomposition. Для data layer - error mapping, threading, cancellation и разделение DTO/domain.

**Важно:** Android bugs часто появляются из-за lifecycle и ownership состояния, а не только из-за неправильной business logic.

## Как давать хороший review feedback?

Хороший review feedback конкретный, уважительный и actionable. Он объясняет, почему проблема важна, и отделяет required changes от suggestions.

Полезные привычки:

- указывать конкретную проблему;
- объяснять risk или trade-off;
- задавать вопросы, когда intent неясен;
- избегать личного тона;
- предпочитать маленькие actionable comments;
- помечать optional ideas как suggestions;
- признавать, когда решение является judgment call.

Примеры тона:

- Required: "This can leak `Activity` because the object is Singleton-scoped. Can we use `@ApplicationContext` or move this dependency closer to the screen scope?"
- Suggestion: "This mapper is getting large. Maybe we can split formatting from API mapping?"
- Question: "Is this event expected to survive configuration change?"

**Главная мысль:** review comments должны помогать улучшить код, а не заставлять автора защищаться.

## Common code review comments

Neutral review comments проще применить, когда они ясно описывают concern:

- "Can we move this logic out of the UI layer?"
- "This looks like state rather than a one-off event."
- "This may run on the main thread."
- "Can we add a test for this edge case?"
- "This abstraction seems premature. Is there a real second use case?"
- "Can we map this DTO before exposing it outside the data layer?"
- "What happens here on retry or configuration change?"
- "Can we make the error state explicit in `UiState`?"

Эти comments - starting points. Лучший review feedback включает причину и ожидаемое направление, а не только требуемое изменение.

## Что делает pull request хорошим?

Хороший pull request достаточно маленький для review, сфокусирован на одной теме и объяснен в понятном description. Он не смешивает unrelated refactoring с feature changes, если refactoring не нужен для самой feature.

Полезное PR description обычно включает:

- что изменилось;
- почему это изменилось;
- как это было протестировано;
- screenshots или recordings для UI changes;
- known limitations или follow-up work.

Хорошие PR уменьшают guesswork для reviewer. Они делают важные решения видимыми и сохраняют diff сфокусированным.

**Коротко:** хороший PR сфокусирован, объяснен, протестирован и достаточно мал для осмысленного review.
