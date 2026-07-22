# OAuth 2.0, PKCE и управление токенами

Нативному Android-приложению нужен authorization flow для public client, который не может безопасно хранить client secret. Статья будет посвящена Authorization Code Flow with PKCE и жизненному циклу Android-сессии, а не полному разбору спецификаций OAuth и OpenID Connect.

## OAuth 2.0 и OpenID Connect

**TODO:** На уровне, важном для Android, разделить делегированную авторизацию, аутентификацию и получение информации об идентичности.

## Модель авторизации нативного приложения

**TODO:** Объяснить public clients, обработку redirects, внешние authorization services и ограничения client secret.

## Authorization Code Flow with PKCE

**TODO:** Описать обмен authorization code, code verifier и challenge, а также проверку state, nonce и redirect.

## Аутентификация через браузер

**TODO:** Рассмотреть flow через системный браузер или Custom Tabs, общее состояние аутентификации и безопасный возврат в приложение.

## Почему login во встроенном WebView обычно не подходит

**TODO:** Подготовить объяснение рисков для учетных данных, требований провайдера, изоляции сессии и отсутствия security context браузера.

## Access tokens

**TODO:** Определить их назначение, audience, scope и короткий срок жизни с точки зрения мобильного клиента.

## Refresh tokens

**TODO:** Рассмотреть их повышенную чувствительность, rotation, reuse detection и зависимость от политики сервера.

## Истечение срока действия токенов

**TODO:** Объяснить проактивную и реактивную обработку expiration, clock skew и границы ошибок.

## Безопасное хранение токенов

**TODO:** Связать срок жизни и чувствительность токенов с архитектурой хранения на основе Android Keystore.

## Добавление авторизации в запросы

**TODO:** Обозначить точку добавления request headers без дублирования общей темы interceptors.

## Обновление токенов

**TODO:** Описать координацию refresh, атомарное обновление сессии, retries и обработку terminal failure.

## Конкурентные запросы и single-flight refresh

**TODO:** Объяснить, как одна refresh-операция обслуживает несколько неуспешных запросов без races и refresh storm.

## OkHttp interceptor и authenticator

**TODO:** Сравнить зоны ответственности и зарезервировать будущую ссылку на отдельную статью про OkHttp Interceptors в разделе Networking.

## Обработка `401 Unauthorized`

**TODO:** Отличить истекшие credentials от отозванной сессии, недостаточных прав и ошибок, которые нельзя повторять.

## Logout и отзыв токенов

**TODO:** Рассмотреть локальную очистку сессии, server-side revocation при наличии поддержки и ожидания от browser session.

## Смерть процесса и восстановление сессии

**TODO:** Определить минимальное сохраняемое состояние и безопасное восстановление после пересоздания процесса Android.

## Ограничения JWT

**TODO:** Объяснить, почему формат токена не заменяет validation, стратегию отзыва, безопасное хранение и server-side authorization.

## Распространенные ошибки реализации

**TODO:** Собрать Android-ошибки, связанные со встроенными credentials, redirects, хранением, refresh races, логированием и retry loops.

## Связанные темы

- [Android Keystore и безопасное хранение](keystore-secure-storage.md)
- [Основы безопасности Android](index.md)
- [HTTPS, TLS и сертификаты](https-tls-certificates.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)

<!-- TODO: Добавить ссылку на отдельную статью про OkHttp Interceptors, когда она появится в разделе Networking. -->
