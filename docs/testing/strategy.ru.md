# Testing Strategy

Testing strategy помогает выбирать, что тестировать в первую очередь, какие уровни тестов использовать и как сохранять test suite быстрым и устойчивым.

## Приоритеты тестирования

### Что тестировать в первую очередь?

В первую очередь стоит тестировать код с высокой бизнес-ценностью и высоким риском: business logic, use cases, mappers, validators, reducers, error mapping и `ViewModel` state transitions.

Не всё нужно покрывать одинаково. Хорошая стратегия начинается с вопросов: что чаще ломается, что дорого сломать в production, где есть сложные условия, edge cases, деньги, авторизация, offline/cache или critical user flow.

UI и framework glue обычно тестируют выборочно, а не пытаются unit-тестами покрыть каждую `Activity` или composable. Важнее проверять observable behavior, а не private implementation details.

**Коротко:** prioritize tests by risk and value: business logic, mapping, state transitions and critical flows first, then UI/integration tests for important user scenarios.

### Unit tests vs UI tests

Unit tests проверяют маленькие части логики быстро и изолированно: use cases, mappers, validators, reducers, `ViewModel` logic, error handling. Они дешёвые, быстрые и хорошо подходят для большинства бизнес-логики.

UI tests проверяют поведение приложения ближе к пользователю: отображение экрана, клики, navigation, формы, happy path и критичные regression scenarios. Но они медленнее, дороже в поддержке и чаще flaky.

Практичный подход: большую часть логики покрывать unit tests, а UI tests оставлять для ключевых пользовательских сценариев, где важно проверить интеграцию UI + state + navigation.

**Коротко:** unit tests are fast and good for logic, UI tests are slower but useful for critical user flows and integration behavior.

### Mocks vs fakes

Mock - тестовый объект, который обычно проверяет interactions: был ли вызван метод, с какими параметрами, сколько раз.

Fake - упрощённая рабочая реализация dependency, например in-memory repository или test data source.

В Android обычно удобнее предпочитать fakes там, где это просто: тест получается ближе к реальному поведению и меньше зависит от внутренних вызовов. Mocks полезны точечно, когда важно проверить конкретное взаимодействие, например analytics event, navigation callback или retry call.

**Важно:** если mock-ать всё подряд, тест становится хрупким и начинает проверять implementation details, а не поведение. Хороший тест обычно задаёт input/action и проверяет observable output/state.

**Коротко:** prefer fakes for readable behavior-based tests and use mocks only when interaction verification is actually important.

### Test pyramid / testing priorities

Test pyramid - идея, что большинство тестов должны быть быстрыми unit tests, меньше должно быть integration tests, и ещё меньше - дорогих end-to-end/UI tests.

Для Android это обычно означает: много unit tests для domain/data/`ViewModel` логики, умеренное количество integration tests для repository/database/network boundaries, и небольшое количество UI tests для критичных flows.

Приоритеты: business-critical logic, state transitions, error cases, edge cases, mapping between layers, persistence/migrations, authentication/payment-like flows и баги, которые уже ломались раньше.

**Коротко:** test pyramid keeps the suite fast and stable: many unit tests, fewer integration tests, and a small number of UI/E2E tests for critical paths.
