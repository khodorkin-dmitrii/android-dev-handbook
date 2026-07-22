# HTTPS, TLS и сертификаты

HTTPS - стандартная основа защиты трафика между Android-приложением и удаленными сервисами. Android и OkHttp уже предоставляют безопасные TLS defaults для обычных публичных HTTPS endpoints. Код приложения обычно должен задавать политику поверх этих defaults, а не заменять проверку сертификатов собственной сетевой реализацией.

## Что защищает HTTPS

Корректно проверенный HTTPS обеспечивает три основных свойства:

- **Конфиденциальность:** посредники обычно не могут прочитать payload приложения.
- **Целостность:** изменение защищенного трафика обнаруживается.
- **Аутентификация сервера:** клиент проверяет, что certificate chain доверена и подходит запрошенному hostname.

HTTPS не доказывает корректность backend, не авторизует пользователя для конкретной операции и не защищает ответ после сохранения или логирования. Malware или instrumentation внутри скомпрометированного устройства могут увидеть plaintext в процессе. TLS также не скрывает все metadata: наблюдателю могут быть доступны destination IP, время и объем трафика, а видимость hostname зависит от согласованного протокола и инфраструктуры.

## TLS handshake на высоком уровне

Упрощенное установление соединения выглядит так:

1. Клиент подключается к серверу.
2. Клиент и сервер согласуют поддерживаемые параметры TLS.
3. Сервер отправляет certificate chain.
4. Клиент проверяет цепочку, свойства сертификатов и hostname.
5. Обе стороны устанавливают session keys.
6. Начинается передача зашифрованных данных приложения.

Современные TLS-конфигурации обычно используют ephemeral key agreement и обеспечивают forward secrecy, поэтому последующая компрометация долгоживущего серверного ключа не расшифровывает автоматически записанные ранее сессии. Практическая задача Android-разработчика - использовать актуальный и правильно настроенный TLS stack платформы, а не реализовывать handshake самостоятельно.

## Серверные сертификаты

Серверный X.509 certificate связывает public key с идентификаторами и содержит issuer, срок действия, extensions и подпись CA. DNS-идентификаторы указываются в Subject Alternative Name. Запрошенный host должен присутствовать там согласно hostname-matching rules; устаревший subject common name не заменяет корректный SAN.

Одного действующего срока недостаточно. Подпись, назначение и цепочка до принятого trust anchor должны быть корректны, сертификат должен совпадать с hostname, а применимые проверки revocation и platform policy - проходить. Сервер также должен отправлять leaf certificate и необходимые intermediate certificates в правильном порядке.

## Центры сертификации

Certificate authority подписывает сертификаты в рамках public-key infrastructure. Принятые Android корневые сертификаты являются **trust anchors**. Доверие root означает принятие корректных цепочек под ним в рамках ограничений платформы и сертификатов, а не доверие каждому серверу этой организации.

Public CAs обслуживают обычные Internet endpoints. Private enterprise или development CAs могут быть оправданы в контролируемой среде, но добавление такого CA расширяет набор идентификаторов, способных аутентифицировать сервер перед приложением, то есть увеличивает границу доверия.

## Цепочки сертификатов

Сервер обычно отправляет leaf certificate и один или несколько intermediate:

```text
Trusted root CA
    -> Intermediate CA
        -> api.example.com
```

Root обычно уже находится в trust store клиента и сервером не отправляется. Клиент строит и проверяет путь от leaf до принятого root. Отсутствующий intermediate может сломать Android-клиент, даже если desktop browser работает, поскольку браузер мог закешировать или отдельно загрузить недостающий сертификат. Server chain нужно тестировать независимо.

## Проверка имени хоста

Chain validation и hostname verification отвечают на разные вопросы:

- Ведет ли эта корректная certificate chain к доверенному CA?
- Подходит ли leaf certificate именно серверу, который запросил клиент?

Сертификат только для `files.example.net` должен быть отклонен при подключении к `api.example.com`, даже если оба используют один доверенный CA. Отключение hostname verification позволяет любому сертификату от доверенного CA выдать себя за запрошенный endpoint.

## Хранилище доверия Android

По умолчанию сетевые stacks Android используют platform trust anchors. Доступные roots и TLS capabilities зависят от Android version, security update и устройства, поэтому server compatibility нужно проверять на поддерживаемой матрице.

Доверие приложения можно декларативно настроить через Network Security Configuration. Принятие user-installed CAs зависит от target behavior и configuration приложения, поэтому нельзя считать одно правило верным для всех версий ОС. Явное добавление system, user или bundled CAs меняет границу доверия. Для публичных production services предпочтителен system store, а private trust anchors следует добавлять только по документированному требованию.

## OkHttp и platform TLS

Обычному OkHttp client не нужны пользовательские TLS-объекты:

```kotlin
val client = OkHttpClient.Builder()
    .build()
```

OkHttp делегирует проверку certificate chain и hostname интеграции с платформой и применяет безопасные defaults. Разработчикам обычно не следует реализовывать или заменять `X509TrustManager`, `SSLSocketFactory` и `HostnameVerifier`. Для private PKI сначала стоит использовать Network Security Configuration, если это возможно, и провести экспертное review.

## Network Security Configuration

Конфигурация подключается в manifest:

```xml
<application
    android:networkSecurityConfig="@xml/network_security_config"
    android:usesCleartextTraffic="false"
    ... />
```

Следующий production baseline запрещает cleartext. Debug override добавляет user-installed CAs только при `android:debuggable=true`, позволяя использовать контролируемый inspection proxy без изменения release trust:

```xml
<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false" />

    <debug-overrides>
        <trust-anchors>
            <certificates src="user" />
        </trust-anchors>
    </debug-overrides>
</network-security-config>
```

`android:usesCleartextTraffic="false"` задает общую политику приложения, а `cleartextTrafficPermitted` позволяет определить base или domain-specific rules для сетевых stacks, поддерживающих конфигурацию. Если legacy host действительно требует HTTP, ограничьте исключение этим доменом и запланируйте удаление. Локальный proxy CA нельзя добавлять в production trust anchors.

## Debug-сертификаты и локальные proxy-инструменты

Charles, Proxyman, mitmproxy и похожие инструменты завершают TLS-соединение устройства и предъявляют сертификат, подписанный локально установленным proxy CA. Инспекция работает, только если debug application доверяет этому CA. Release builds должны сохранять обычное production trust и тестироваться отдельно.

Certificate pinning добавляет еще одну проверку и может по-прежнему отклонять proxy connection. Если проекту нужна инспекция pinned endpoints, используйте явное разделение build variants под контролем команды. Не добавляйте runtime switch или глобальный bypass, способный попасть в production.

## Распространенные небезопасные реализации

**Намеренно небезопасный код - никогда не используйте его в приложении:**

```kotlin
val unsafeHostnameVerifier = HostnameVerifier { _, _ -> true }
```

Такой код принимает доверенный сертификат для неверного hostname. Столь же опасен custom trust manager, который успешно завершает проверку любой цепочки. Оба изменения убирают server authentication из TLS и позволяют man-in-the-middle с произвольным или чужим сертификатом выдать себя за сервис.

Игнорирование TLS errors не является временным исправлением. Нужно исправить server chain, hostname, часы устройства, trust configuration или контролируемый development CA. Не публикуйте полноценный accept-all trust manager даже как sample или test utility, который затем может попасть в release sources.

## Практические рекомендации для ревью

- Используйте HTTPS для всех чувствительных endpoints и запрещайте cleartext по умолчанию.
- Не меняйте стандартную проверку сертификатов и hostname.
- Предпочитайте declarative trust configuration собственному TLS-коду.
- Ограничивайте proxy CAs и другие test trust только debuggable builds.
- Тестируйте поддерживаемые Android versions, hostnames, redirects и server-chain deployment.
- Отслеживайте renewal сертификатов и изменения intermediate chain до production rollout.

**Главная мысль:** TLS - стандартная граница защиты трафика. Custom validation расширяет или удаляет эту границу, поэтому требует конкретного обоснования, тщательного тестирования и явного владельца.

## Связанные темы

- [Основы безопасности Android](index.md)
- [Certificate Pinning](certificate-pinning.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
- [Network Inspection](../tools/network-inspection.md)
