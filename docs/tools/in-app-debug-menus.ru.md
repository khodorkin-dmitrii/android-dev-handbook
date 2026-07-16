# In-App Debug Menus

Внутреннее debug menu превращает сложное приложение в систему, состояние которой можно исследовать. Это особенно полезно, когда QA, support или удаленный разработчик не могут подключить Android Studio.

## Полезные возможности

Сфокусированное меню может показывать:

* environment, версию, build variant и commit SHA;
* feature flags и состояние account/session;
* последние logs и network requests;
* безопасные summaries local storage или database;
* сброс cache/session и predefined application states;
* симуляцию ошибок, offline, empty state и sync;
* переходы на внутренние экраны;
* metadata устройства и приложения, screenshots, screen recording и diagnostic export.

Действия нужно группировать по задачам, а destructive operations подтверждать явно. Неорганизованный drawer с десятками кнопок быстро становится еще одной ненадежной подсистемой.

```text
Debug UI
   ↓
Debug Actions / Commands
   ↓
Application services, repositories, feature flags and diagnostics
```

UI должен вызывать явные debug commands, а не произвольно обращаться к repositories или напрямую менять database.

## Подходы к реализации

### Custom debug menu

Собственный экран дает полный контроль над Compose UI, navigation, design system, authorization и redaction. Он хорошо подходит для project-specific операций и может зависеть только от стабильных application-owned interfaces.

Цена подхода - разработка и поддержка. Стоит заранее определить ownership модулей, registry действий, подтверждение destructive operations и тесты, чтобы меню не превратилось в случайный набор shortcuts.

### Beagle

Beagle - поддерживаемая customizable debug-menu библиотека с configurable modules, logging, OkHttp inspection, metadata, screen capture и bug-report actions. Официальные UI integrations основаны на Activity/Fragment/View и включают drawer, dialog и bottom sheet. Compose-приложение может открыть или встроить такой UI, но это не равнозначно native Compose-first контракту.

Beagle предоставляет no-op artifacts для production variants. Перед внедрением все равно нужно оценить lifecycle hooks, требования к theme, набор зависимостей, обработку данных и соответствие архитектуре приложения.

### Hyperion

Hyperion - исторически важный plugin drawer, который мог открываться shake gesture и показывать build data, files, preferences, SQLite, recordings и другие plugins.

Для новых проектов его нужно считать legacy/reference:

* он связан прежде всего с View-based Android era;
* release и integration model устарели;
* встроенный UI inspection не понимает Compose;
* сегодня его главная ценность - демонстрация концепции debug drawer.

## Build boundaries и безопасность

Предпочтителен отдельный debug/internal source set или module. Production artifacts должны исключать debug implementations, где это возможно, а не просто скрывать кнопку входа. Release no-op implementations нужны только при необходимости общего API.

Internal builds все равно требуют authentication, безопасного переключения environments, redaction, контроля destructive actions и защиты production-like data. Мощное меню является operational capability, а не поводом ослаблять безопасность.

## См. также

* [QA-Friendly Debug Builds](qa-debug-builds.md)
* [Logging and Diagnostic Data](logging-diagnostics.md)
* [Network Inspection](network-inspection.md)
* [Gradle & Build System](../android/gradle-build-system.md)

