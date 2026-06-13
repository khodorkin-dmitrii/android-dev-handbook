# Legacy DI

Legacy DI-подходы всё ещё встречаются в Android-проектах, особенно рядом с MVP, Moxy, RxJava и старой multi-module архитектурой.

## Legacy frameworks

### Dagger vs Toothpick

Dagger и Toothpick - оба DI frameworks, но отличаются моментом проверки graph-а и моделью работы.

Dagger строит dependency graph на этапе компиляции, генерирует код и даёт compile-time validation. Если binding отсутствует, scope несовместим или graph нельзя собрать, ошибка обычно появляется при сборке проекта.

Toothpick исторически был runtime DI framework: он проще входил в Android legacy-код, давал scopes и меньше compile-time boilerplate, но часть ошибок обнаруживается только во время выполнения.

Практический trade-off: Dagger/Hilt обычно быстрее и безопаснее для больших production проектов, потому что graph проверяется заранее и нет reflection-heavy runtime lookup. Toothpick мог быть удобен в legacy-проектах с MVP/Moxy и кастомными scope-ами, но требует дисциплины и хороших тестов, чтобы не ловить DI ошибки поздно.

В modern Android чаще выбирают Hilt поверх Dagger. Если в проекте уже есть Toothpick, его обычно не заменяют механически: сначала изолируют composition root, interfaces и scopes, а затем постепенно переносят feature за feature.

**Коротко:** Dagger gives generated code and compile-time graph validation, while Toothpick is more runtime-oriented and simpler for some legacy setups, but with later error detection.

### Moxy dependencies / legacy patterns

Moxy - legacy Android MVP framework, который помогал отделять Presenter от `Activity` / `Fragment` и переживать configuration changes через generated delegate/proxy-код.

В старых Android-проектах Moxy часто встречается вместе с MVP, Cicerone/RxJava и Dagger/Toothpick. View обычно описывалась интерфейсом, Presenter держал presentation logic, а `Activity` / `Fragment` реализовывали View interface и вызывали attach/detach через lifecycle.

Главный риск Moxy/MVP legacy - lifecycle coupling: Presenter может держать reference на View, callbacks могут прийти после уничтожения экрана, а зависимости часто оказываются спрятаны в base classes, custom scopes или service locator-like helpers.

При поддержке такого кода важно не ломать lifecycle contract: сначала понять, кто создаёт Presenter, где происходит injection, как View attach/detach связан с `Fragment` / `Activity` lifecycle и где хранятся subscriptions/disposables.

При миграции на modern Android обычно не переписывают всё сразу. Практичный путь - выделить repository/use case слой, стабилизировать UI contract, заменить Presenter на `ViewModel` там, где feature уже готова к migration, и постепенно перейти к `StateFlow` / `UiState`.

**Коротко:** Moxy is a legacy MVP framework; when refactoring it, first protect lifecycle behavior and then migrate presentation logic toward `ViewModel` and state-driven UI gradually.
