# Context & Resources

`Context` и resources связывают код приложения с Android runtime: ресурсами, system services, theme, configuration и запуском компонентов.

## Context

### Activity Context vs Application Context

`Context` - это доступ к окружению Android-приложения: resources, assets, system services, package info, запуск `Activity` / `Service` / Broadcast и т.д.

`Activity Context` привязан к lifecycle конкретной `Activity` и знает о theme, window и UI-состоянии. Его используют для UI-операций: inflate themed layout, show dialog, start activity from screen, access themed resources.

`Application Context` живёт столько же, сколько процесс приложения. Его используют для долгоживущих объектов: repositories, databases, `DataStore`, analytics, dependency graph, если им не нужен UI/theme конкретной `Activity`.

Главный pitfall: нельзя хранить `Activity Context` в singleton/static object/long-lived component, иначе можно получить memory leak `Activity`. Если нужен `Context` в долгоживущем объекте, чаще безопаснее использовать `applicationContext`.

**Коротко:** `Activity Context` is UI/lifecycle/themed context, `Application Context` is process-level context; avoid storing `Activity Context` longer than Activity lifecycle.

### ContextWrapper

`ContextWrapper` - класс-обёртка над `Context`, который делегирует вызовы базовому `Context`, но позволяет переопределять часть поведения.

Многие Android-классы построены вокруг этой идеи: `ContextThemeWrapper` добавляет или меняет theme, `Activity` тоже является `ContextThemeWrapper`, а `Application` и `Service` наследуются от `ContextWrapper`.

`ContextWrapper` полезен, когда нужно создать `Context` с другой theme/configuration или адаптировать поведение `Context` API без изменения исходного base context.

На практике Android-разработчик чаще сталкивается с ним косвенно: themed inflater, dialog context, localized/configuration context, activity as context.

**Коротко:** `ContextWrapper` wraps another `Context` and delegates to it, while allowing specific behavior like theme or configuration to be overridden.

## Resources

### Resources / configuration / orientation

Resources - API для доступа к ресурсам приложения: strings, drawables, colors, dimensions, layouts, plurals и другим файлам из `res/`.

Configuration описывает текущую конфигурацию устройства и приложения: orientation, locale, screen size, density, night mode, font scale и другие параметры.

Когда configuration меняется, например при rotation, смене языка или dark mode, Android может пересоздать `Activity`, чтобы заново применить подходящие resources из qualifiers: `layout-land`, `values-night`, `values-ru`, `drawable-xhdpi` и т.д.

Orientation - частный случай configuration. При смене portrait/landscape важно не хранить UI state только во `View`, а использовать `ViewModel`, `SavedStateHandle` / `onSaveInstanceState()` или persistent storage в зависимости от типа данных.

Можно обработать часть изменений вручную через `android:configChanges`, но это переносит ответственность на приложение и обычно не должно использоваться как стандартное решение для всех экранов.
