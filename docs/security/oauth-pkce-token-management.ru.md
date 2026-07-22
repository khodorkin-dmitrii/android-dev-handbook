# OAuth 2.0, PKCE и управление токенами

Нативные Android-приложения являются public clients: их binaries и runtime behavior можно исследовать, поэтому встроенный статический client secret не может быть конфиденциальным. Надежная сессия использует flow для public clients, направляет пользователя во внешний доверенный браузер, рассматривает tokens как scoped и revocable credentials и выполняет refresh как явный переход состояния.

## OAuth 2.0 и OpenID Connect

OAuth 2.0 - framework делегированной авторизации. Он позволяет клиенту получить ограниченный доступ к защищенному ресурсу, не собирая пароль владельца ресурса. Сам OAuth не является login protocol.

OpenID Connect (OIDC) добавляет identity layer поверх OAuth 2.0. Приложения обычно используют OIDC для sign-in пользователя, а OAuth access tokens - для авторизации API calls:

- **Access token** разрешает вызовы конкретного resource server в рамках audience и scope.
- **ID token** передает клиенту сведения об authentication event и identity claims.
- **Refresh token** позволяет получить новый access token согласно policy провайдера.

Эти значения не взаимозаменяемы. ID token не является общим API credential, а API не должен принимать token, выпущенный для другой audience.

## Модель авторизации нативного приложения

Установленное Android-приложение не может скрыть общий статический секрет от владельца устройства. Значение внутри APK, resources, native code или remote configuration, доступной каждому installation, является public client credential даже после obfuscation.

Native applications должны использовать зарегистрированные redirect URIs и flows для public clients. Redirect handling должен настолько надежно, насколько позволяют платформа и provider, подтверждать принадлежность ответа инициировавшему приложению через claimed HTTPS redirects или аккуратно зарегистрированные custom schemes. Authorization service обязан проверять точное совпадение redirect URI.

Backend-for-frontend или другой confidential server component находится в другой trust environment, поскольку может защищать service credentials и аутентифицировать server-to-server connections. Добавление такого backend меняет ownership tokens и API architecture, но не делает secret внутри APK конфиденциальным.

## Authorization Code Flow with PKCE

Proof Key for Code Exchange связывает authorization request с экземпляром клиента, который его начал:

1. Создать высокоэнтропийный одноразовый `code_verifier`.
2. Вычислить `code_challenge = BASE64URL(SHA256(code_verifier))`.
3. Открыть authorization request с challenge, `S256` и новым `state`.
4. Пользователь аутентифицируется и подтверждает доступ в authorization service.
5. Приложение получает короткоживущий одноразовый authorization code через проверенный redirect.
6. Приложение обменивает code и исходный verifier на tokens.
7. Authorization server проверяет, что verifier дает сохраненный challenge.

Перехваченный code бесполезен без verifier. Используйте `S256`, cryptographically random verifier для каждой попытки и храните его только во время активной authorization transaction. `state` связывает request и response и защищает от подмены между запросами и CSRF-подобных атак. В OIDC новый `nonce` связывает authentication request с ID token и должен проверяться.

PKCE не проверяет ownership redirect и не заменяет `state`, `nonce`, TLS или backend authorization. Предпочитайте зрелую standards-compliant OAuth/OIDC библиотеку, например AppAuth, если она соответствует provider, вместо ручной сборки protocol requests и token validation.

## Аутентификация через браузер

Native authorization обычно должна открывать системный браузер или browser-backed surface, например Custom Tabs. Приложение не получает пароль пользователя напрямую, пользователь видит origin авторизации, а flow может использовать существующую provider session, password managers, security keys, passkeys и browser security controls.

Standards-compliant client library также надежнее custom URI construction обрабатывает discovery, redirect matching, PKCE encoding и protocol errors. Приложение по-прежнему отвечает за lifecycle state, cancellation, account selection и безопасное persistence после token response.

## Почему login во встроенном WebView обычно не подходит

При authentication через внешнего identity provider WebView является embedded user agent под контролем приложения. Host app может исследовать page content и credential input, а пользователь не способен надежно проверить настоящий origin. Shared provider sessions, password managers, security keys и passkeys могут работать неправильно, а providers могут блокировать embedded authorization.

Это не означает, что любая страница WebView небезопасна. Предупреждение относится именно к embedded surface для ввода credentials или third-party authorization. Используйте поддерживаемый provider внешний browser flow, если только отдельная проверенная first-party authentication architecture не требует другого решения.

## Access tokens

Большинство access tokens являются bearer credentials: для использования достаточно владеть token. Отправляйте его только на предназначенный HTTPS origin и API audience, в header `Authorization`, но не в URL. URLs часто попадают в history, analytics, referrers, screenshots и infrastructure logs.

Ограничивайте scopes и делайте lifetime достаточно коротким для риска продукта. Не отправляйте token одного provider на посторонние hosts и не считайте token действительным только потому, что локально декодированный expiration еще не наступил. Network logging, crash reports, analytics и debug tools должны редактировать authorization headers и token responses.

## Refresh tokens

Refresh tokens обычно живут дольше и несут больший риск, чем access tokens. Provider может ротировать их при каждом использовании, обнаруживать reuse старого token, отзывать token family, привязывать их к client или device signal либо вообще не выдавать.

Клиент обязан атомарно принимать каждый новый token set, включая replacement refresh token. Отказ в refresh - нормальное terminal session state, а не исключение для бесконечных retries. Provider policy определяет expiration, inactivity windows, revocation и срок действия старого refresh token.

## Истечение срока действия токенов

Полезны две стратегии:

- **Proactive refresh:** обновить token незадолго до известного expiry, чтобы сократить ошибки foreground calls.
- **Reactive refresh:** отреагировать на authentication failure после отказа сервера принять credential.

Сбалансированная реализация может сочетать оба подхода. Учитывайте clock skew и не делайте refresh перед каждым request. Источником истины остается сервер, а `401` не доказывает, что token только истек: он может быть отозван, поврежден, выпущен для другой audience или принадлежать invalid session.

## Безопасное хранение токенов

Access token можно оставить только в памяти, если после process death допустима повторная authentication. Refresh token обычно требует более осознанного persistence, когда продукт обещает восстановление сессии или background work. Используйте Keystore-backed encrypted persistence с определенными backup, invalidation, migration и recovery policy вместо plain preferences.

Encryption снижает риск простого extraction и offline inspection, но не скрывает token после загрузки в скомпрометированный процесс. Разделяйте token sets разных accounts, атомарно заменяйте access и refresh tokens и полностью очищайте выбранную сессию при logout. Архитектура хранения описана в [Android Keystore и безопасное хранение](keystore-secure-storage.md).

## Добавление авторизации в запросы

Application interceptor может добавлять актуальный token только к запросам точного API host. Нельзя навсегда кешировать один token или отправлять credentials при redirects и на посторонние origins:

```kotlin
interface TokenStore {
    fun current(): TokenSet?
    fun replace(tokens: TokenSet)
    fun clear()
}

data class TokenSet(
    val accessToken: String,
    val refreshToken: String,
)

class AccessTokenInterceptor(
    private val apiHost: String,
    private val tokenStore: TokenStore,
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        if (request.url.host != apiHost || request.header("Authorization") != null) {
            return chain.proceed(request)
        }

        val accessToken = tokenStore.current()?.accessToken
            ?: return chain.proceed(request)

        return chain.proceed(
            request.newBuilder()
                .header("Authorization", "Bearer $accessToken")
                .build(),
        )
    }
}
```

`TokenStore` должен предоставлять thread-safe snapshots и atomic replacement. Logging interceptors обязаны скрывать `Authorization`. Refresh orchestration находится вне этого interceptor, чтобы обычные requests не запускали независимые refresh calls.

## Обновление токенов

Refresh - это переход состояния сессии:

1. Прочитать один внутренне согласованный token set.
2. Обменять refresh token через отдельный client, который не может рекурсивно вызвать тот же authenticator.
3. Классифицировать результат как success, rejected credentials или transient failure.
4. При успехе атомарно заменить оба token.
5. Очистить или инвалидировать сессию при окончательном отказе provider обновить credentials.
6. Сохранить сессию при transient network failure и вернуть retryable result.

Сохранение нового access token вместе с устаревшим rotated refresh token создает сломанную сессию. Храните полный набор как одну versioned record или transaction.

## Конкурентные запросы и single-flight refresh

Несколько параллельных calls могут одновременно получить `401` для одного token. Если каждый самостоятельно выполняет refresh, rotation refresh token может привести к взаимной invalidation запросов, публикации несогласованных token sets, refresh storm или принудительному logout.

Single-flight coordinator допускает только один refresh одновременно. После входа в critical section он проверяет, не заменил ли другой request уже отклоненный token. В примере используется JVM monitor, потому что OkHttp `Authenticator` синхронный и работает не на main thread:

```kotlin
sealed interface RefreshResult {
    data class Success(val tokens: TokenSet) : RefreshResult
    data object Rejected : RefreshResult
    data object TransientFailure : RefreshResult
}

interface AuthApi {
    fun refresh(refreshToken: String): RefreshResult
}

class TokenRefreshCoordinator(
    private val tokenStore: TokenStore,
    private val authApi: AuthApi,
) {
    private val lock = Any()

    fun refreshAfter(failedAccessToken: String): TokenSet? {
        return synchronized(lock) {
            val current = tokenStore.current() ?: return@synchronized null

            if (current.accessToken != failedAccessToken) {
                return@synchronized current
            }

            when (val result = authApi.refresh(current.refreshToken)) {
                is RefreshResult.Success -> {
                    tokenStore.replace(result.tokens)
                    result.tokens
                }
                RefreshResult.Rejected -> {
                    tokenStore.clear()
                    null
                }
                RefreshResult.TransientFailure -> null
            }
        }
    }
}
```

`AuthApi` должен использовать client без этого authenticator, иначе возникнет recursion. Production code должен передавать различие между rejection и transient failure в session/UI state, поддерживать cancellation и timeouts, делать persistence атомарным и не удерживать посторонние locks во время network I/O. Coroutine-first architecture может реализовать то же single-flight правило через `Mutex` или shared `Deferred` вне синхронного OkHttp callback.

## OkHttp interceptor и authenticator

**Interceptor** изменяет исходящие requests и подходит для добавления текущего authorization header к известному host. Он не должен безусловно выполнять refresh и повторять calls.

**Authenticator** реагирует на server authentication challenges, например `401`, и может построить follow-up request. OkHttp способен вызывать его конкурентно, поэтому необходимы loop prevention и общий refresh coordinator.

```kotlin
class AccessTokenAuthenticator(
    private val apiHost: String,
    private val tokenStore: TokenStore,
    private val refreshCoordinator: TokenRefreshCoordinator,
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.request.url.host != apiHost || responseCount(response) >= 2) {
            return null
        }

        val authorization = response.request.header("Authorization") ?: return null
        val failedToken = authorization.removePrefix("Bearer ")
        if (failedToken == authorization) return null

        val current = tokenStore.current() ?: return null
        val tokens = if (current.accessToken != failedToken) {
            current
        } else {
            refreshCoordinator.refreshAfter(failedToken) ?: return null
        }

        return response.request.newBuilder()
            .header("Authorization", "Bearer ${tokens.accessToken}")
            .build()
    }

    private fun responseCount(response: Response): Int {
        var count = 1
        var prior = response.priorResponse
        while (prior != null) {
            count++
            prior = prior.priorResponse
        }
        return count
    }
}
```

Этот сокращенный sample повторяет authenticated request не более одного раза, использует token, уже обновленный другим call, и возвращает `null`, если challenge нельзя удовлетворить. Здесь опущены provider-specific errors, non-repeatable request bodies, cancellation, metrics, account switching, persistence implementation и UI session events. Безопасность повторного выполнения каждой API operation нужно проверять отдельно.

## Обработка `401 Unauthorized`

Конечный decision flow предотвращает loops:

1. Проверить, что неуспешный request действительно использовал access token для ожидаемого host.
2. Остановиться, если request уже повторялся.
3. Использовать более новый token, если другой request уже обновил сессию.
4. Выполнять refresh только при наличии refreshable session.
5. Один раз повторить исходную operation с новым token.
6. Завершить сессию, если refresh credentials отклонены.
7. Отличить transient network failure от invalid credentials.

`401` может означать отсутствующий, истекший, отозванный, поврежденный, неверно подписанный или wrong-audience token либо provider-specific invalid session. Недостаток permissions обычно представлен `403`, но источником истины служит backend contract. Нельзя бесконечно выполнять refresh или превращать каждый authorization failure в logout без классификации.

## Logout и отзыв токенов

Logout состоит из нескольких связанных, но разных действий:

- прекратить добавление выбранного token set к новым requests;
- атомарно очистить persisted и in-memory session state;
- отменить или изолировать in-flight authenticated work и account-scoped caches;
- отозвать refresh или access tokens в authorization service при наличии поддержки;
- при необходимости вызвать OIDC end-session behavior provider.

Local app logout, token revocation и identity-provider browser logout - разные операции. Очистка tokens приложения не обязательно завершает provider session в системном браузере. Ожидаемый UX и privacy behavior нужно определить явно, особенно для shared devices и нескольких accounts.

## Смерть процесса и восстановление сессии

Сохраняйте только token state, необходимое продукту. После restart расшифруйте одну versioned record, убедитесь, что access и refresh tokens относятся к одному account и session, затем выполните refresh или потребуйте authentication при неполном либо отклоненном состоянии.

Authorization codes, `state`, `nonce` и PKCE verifiers являются временными transaction data. Храните их только пока конкретный flow может завершиться, привязывайте redirect к этому flow и очищайте брошенное или использованное state. В приложении с несколькими accounts нужны account-scoped token records и atomic selected-account transition.

## Ограничения JWT

JWT - формат token, а не authorization architecture, и не каждый OAuth token является JWT. Base64url decoding только разбирает читаемые claims, но не проверяет signature, issuer, audience, expiry, nonce или authorization.

Backend обязан валидировать access tokens и контролировать permissions на ресурсы. Android-клиент не должен выдавать security-sensitive capability на основе непроверенного decoded claim. Signed JWT обычно encoded, а не encrypted, поэтому чувствительный plaintext нельзя помещать в claims только из-за наличия подписи.

JWT не решает автоматически revocation или logout. Для ID tokens используйте standards-compliant OIDC library и provider metadata вместо ad hoc parsing или собственной signature logic.

## Распространенные ошибки реализации

- Встроенный постоянный client secret в APK.
- Сбор пароля внешнего provider внутри приложения или WebView.
- Отсутствующий PKCE, повторное использование verifier или слабая random generation.
- Отсутствие проверки точного redirect, `state` или OIDC `nonce`.
- Хранение tokens в plain preferences или логирование headers и token responses.
- Отправка bearer token на посторонний host или размещение его в URL.
- Refresh при каждом `401` без классификации ошибки.
- Параллельные refresh с rotating refresh token.
- Authenticator loop или неограниченное повторение request.
- Неатомарное обновление access и refresh tokens.
- Сохранение tokens, caches или in-flight work после logout или account switch.
- Доверие decoded JWT claims без standards-compliant validation.

## Практическая схема архитектуры

```text
Browser / Custom Tab
    -> Authorization service
    -> Validated redirect to Android app
    -> Authorization code + PKCE exchange
    -> Atomic token store
    -> OkHttp request authorization
    -> Single-flight refresh
    -> Atomic session update or logout
```

Основные принципы стабильны: приложение является public client и не содержит confidential client secret, использует Authorization Code Flow with PKCE во внешнем браузере, короткоживущий access token, защищенное persistence refresh token, один coordinated и bounded refresh, а authoritative authorization оставляет backend.

## Связанные темы

- [Android Keystore и безопасное хранение](keystore-secure-storage.md)
- [Основы безопасности Android](index.md)
- [HTTPS, TLS и сертификаты](https-tls-certificates.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
