# Certificate Pinning

Certificate pinning сужает набор серверных идентификаторов, которым приложение доверяет помимо стандартной проверки платформы. Он может снизить отдельные риски, связанные с certificate authorities, но добавляет требования к deployment, recovery, testing и rotation. Pinning - это дополнительное ограничение после обычной TLS validation, а не обязательная настройка каждого Android-приложения.

## Какую задачу решает pinning

Стандартный TLS принимает корректную certificate chain, ведущую к любому trust anchor, разрешенному приложением. Pinning добавляет требование для конкретного host: хотя бы один сертификат в уже проверенной peer chain должен содержать ожидаемый public key. Это может снизить риск ошибочно или злонамеренно выпущенного сертификата или неожиданно доверенного CA.

Pinning не заменяет chain validation и hostname verification. OkHttp проверяет pins после успешного TLS handshake, поэтому pinned self-signed certificate всё равно будет отклонен, если trust manager не принимает его цепочку. Pinning также не защищает полностью скомпрометированный client runtime, не исправляет backend authorization и не возвращает утекшие tokens.

## Certificate pinning и public-key pinning

Приложение концептуально может закрепить точный сертификат или его public key. Pin точного сертификата меняется при каждой его замене, даже если новый сертификат использует прежний ключ. Public-key pinning хранит хеш Subject Public Key Info (SPKI) сертификата, поэтому обновленный сертификат может продолжить соответствовать pin при сохранении ключа.

OkHttp `CertificatePinner` использует SPKI hashes. Это дает больше свободы при renewal, однако бесконечное повторное использование ключа увеличивает ущерб от его компрометации. Команде всё равно нужны запланированная rotation и backup pins. Browser HPKP - deprecated web mechanism; application-level конфигурация OkHttp работает в другом контексте deployment и recovery, хотя формат хеша связан с HPKP.

## OkHttp `CertificatePinner`

```kotlin
val certificatePinner = CertificatePinner.Builder()
    .add(
        "api.example.com",
        "sha256/PRIMARY_PIN",
        "sha256/BACKUP_PIN",
    )
    .build()

val client = OkHttpClient.Builder()
    .certificatePinner(certificatePinner)
    .build()
```

Placeholder values нужно заменить на Base64-encoded SHA-256 hashes от SPKI сертификатов. Pins - это конфигурация, а не секреты. Exact pattern соответствует одному hostname. У wildcard patterns строгие правила для крайнего левого label, поэтому нужно явно настроить и проверить каждый production hostname, а не предполагать, что pattern его охватывает.

Получайте pins по документированной OkHttp процедуре в доверенной сети, а затем сверяйте выбранные ключи с владельцем инфраструктуры. Механическое копирование всех hashes из failure message без понимания leaf, intermediate, ownership и rotation policy создает хрупкую или слишком широкую конфигурацию.

## Резервные pins

Надежная политика обычно принимает как минимум primary и backup pin. Резервный pin должен соответствовать независимо контролируемому ключу, который безопасно хранится и действительно может получить сертификат и попасть на сервер при восстановлении. Hash без доступа к соответствующему private key и issuance path не является рабочим backup.

Закрепление каждого сертификата в текущей цепочке не гарантирует надежность. Intermediates могут быть общими, меняться по решению CA или находиться вне контроля приложения. Нужно явно определить, какими ключами владеет организация и какие изменения инфраструктуры может пережить mobile release.

## Ротация сертификатов

Безопасная rotation использует пересекающийся rollout:

1. Создать и защитить новый ключ, получить его pin.
2. Выпустить версию приложения, принимающую старый и новый pins.
3. Дождаться достаточного adoption с учетом поддерживаемых старых версий.
4. Развернуть новый server certificate и key.
5. Проверить production traffic и совместимость старых clients.
6. Удалить устаревшие pins только в следующем release, когда это позволяет политика поддержки.

Server configuration меняется за минуты, но mobile release требует review, а часть пользователей никогда не обновится. Самая старая поддерживаемая версия приложения поэтому является частью certificate operations.

## Стратегия истечения срока и восстановления

До включения pinning нужно подготовиться к истекшему сертификату, скомпрометированному ключу, ошибочному pin, экстренной миграции и постоянно устаревшим clients. Неверный pin способен вызвать полный outage, при котором приложение не достигнет даже сервиса доставки новой конфигурации.

Полезные меры включают независимо используемые backup pins, overlapping validity, staged mobile и server rollout, monitoring и определенную minimum supported version. Alternative endpoint является recovery path только в том случае, если его identity и behavior заранее спроектированы и защищены. Загрузка произвольного replacement pin через уже недоверенное соединение уничтожает смысл pinning.

У remote configuration та же bootstrap problem. Она может выбирать среди pins или policies, уже аутентифицированных установленным приложением, но не может безопасно создать новый trust anchor после отказа всех pinned paths без отдельного authenticated recovery mechanism.

## Операционные риски

- Pin mismatch может заблокировать весь API traffic для затронутых версий.
- CDN и сторонние services могут ротировать keys вне контроля мобильной команды.
- Server, infrastructure, security, QA и mobile release schedules должны быть согласованы.
- Старые версии приложения остаются у пользователей после того, как их pins должны были устареть.
- Изменения certificate и chain требуют monitoring, alerts, владельцев и проверенного runbook.

Не закрепляйте сторонние endpoints, если provider явно не поддерживает это и не дает стабильный operational contract. Сторона, меняющая сертификат, должна участвовать в lifecycle pins.

## Влияние на QA и debugging proxies

Interception proxy предъявляет свою certificate chain, поэтому pinned production host обычно ее отклоняет, даже когда debug app доверяет proxy CA. Глобальное отключение pinning или пользовательский switch делают production behavior неопределенным.

Если нужна инспекция трафика, используйте отдельный контролируемый debug variant с отдельным созданием client или trust configuration. Release variants обязаны сохранять production pinning. Автоматические проверки должны подтверждать, что debug exceptions, proxy CAs и bypass configuration отсутствуют в release artifacts.

При использовании declarative pins из Network Security Configuration Android может обходить их для цепочек, которым доверяет через `debug-overrides`. Это не отключает автоматически отдельно настроенный OkHttp `CertificatePinner`.

## Тестирование pinning

| Сценарий | Ожидаемый результат | Типичный уровень |
| --- | --- | --- |
| Корректный primary pin | Соединение успешно | Integration |
| Корректный backup pin | Соединение успешно | Integration или staging |
| Доверенная цепочка с unpinned key | Pinning failure | Integration |
| Некорректная certificate chain | TLS failure до проверки pin | Integration |
| Hostname mismatch | TLS failure до проверки pin | Integration |
| Старый и новый pins во время rotation | Оба deployment работают | Staging |
| Release variant | Production pin policy присутствует | Build/integration |
| Debug proxy | Работает только с ожидаемой debug policy | Manual/integration |
| Поддерживаемая старая версия | Поведение соответствует rotation plan | Staging/device matrix |

Unit tests могут проверять выбор configuration и host-pattern logic. Для реального TLS, chain building, proxy и rotation нужны integration tests или staging infrastructure.

## Когда pinning оправдан

Pinning может быть оправдан для ценных финансовых или identity operations, явного regulatory или enterprise requirement, либо конкретной threat model, где сокращение доверия CA дает заметную пользу. Лучшие кандидаты используют контролируемую first-party infrastructure и уже имеют зрелые key management, monitoring, staged rollout и emergency recovery.

Решение должно называть атакующего, защищаемый asset, допустимый availability risk и команды, отвечающие за будущую rotation. Формулировка «больше безопасности» не является достаточным требованием.

## Когда достаточно стандартного TLS

Стандартный platform TLS часто предпочтительнее при обычном риске приложения, сторонней или CDN-managed infrastructure, отсутствии возможности согласовать certificate rotation и в продуктах, где риск outage превышает пользу от дополнительного ограничения доверия. Корректные chain validation, hostname verification, cleartext blocking, dependency maintenance и backend authorization остаются надежной базой.

> Pinning - не только решение в клиентском коде. Это долгосрочное операционное обязательство mobile, backend, infrastructure, security и QA команд.

## Связанные темы

- [HTTPS, TLS и сертификаты](https-tls-certificates.md)
- [Основы безопасности Android](index.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
- [Network Inspection](../tools/network-inspection.md)
