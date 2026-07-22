# Certificate Pinning

Certificate pinning narrows which server identities an application accepts beyond standard platform trust. It can reduce specific certificate-authority risks, but it also creates deployment, recovery, testing, and rotation obligations. Pinning is an additional restriction after normal TLS validation, not a mandatory default for every Android application.

## What problem pinning tries to solve

Standard TLS accepts a valid certificate chain anchored in any trust anchor allowed by the application. Pinning adds a host-specific requirement that at least one certificate in the already valid peer chain has an expected public key. This can reduce exposure to a mistakenly or maliciously issued certificate or an unexpectedly trusted CA.

Pinning does not replace chain validation or hostname verification. OkHttp evaluates pins after a successful TLS handshake, so a pinned self-signed certificate is still rejected unless the trust manager accepts its chain. Pinning also cannot secure a fully compromised client runtime, repair backend authorization, or recover leaked tokens.

## Certificate pinning vs public-key pinning

An application can conceptually pin an exact certificate or its public key. Exact-certificate pinning changes whenever that certificate is replaced, even if the replacement uses the same key. Public-key pinning stores a hash of the certificate's Subject Public Key Info (SPKI), so a renewed certificate can continue to match when it reuses the key.

OkHttp's `CertificatePinner` uses SPKI hashes. This gives more renewal flexibility, but indefinite key reuse increases the impact of key compromise. Teams still need planned key rotation and backup pins. Browser HPKP is a deprecated web mechanism; application-level OkHttp configuration has different deployment and recovery constraints even though the hash format is related.

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

The placeholder values must be replaced with Base64-encoded SHA-256 hashes of certificate SPKI values. Pins are configuration, not secrets. Exact patterns match one hostname. Wildcard patterns have precise leftmost-label behavior, so configure and test every production hostname rather than assuming a pattern covers it.

Use OkHttp's documented procedure to obtain the peer-chain pins on a trusted network, then verify the selected keys with the infrastructure owner. Copying every hash from a failure message without understanding leaf, intermediate, ownership, and rotation policy can create a fragile or overly broad configuration.

## Backup pins

A resilient policy normally accepts at least a primary and a backup pin. The backup should represent an independently controlled key that is stored safely and can actually be certified and deployed during recovery. A hash without access to the corresponding private key and issuance path is not a usable backup.

Pinning every certificate in today's chain is not automatically resilient. Intermediates may be shared, changed by the CA, or outside the application's control. Decide explicitly which keys the organization owns and which infrastructure changes the mobile release can tolerate.

## Certificate rotation

A safe rotation is an overlapping deployment:

1. Generate and protect the new key and obtain its pin.
2. Release an app version accepting both old and new pins.
3. Wait for sufficient adoption while measuring supported old versions.
4. Deploy the new server certificate and key.
5. Verify production traffic and old-client compatibility.
6. Remove obsolete pins only in a later app release when policy permits.

Server configuration can change in minutes, but mobile releases take review time and users may never update. The oldest supported application version is therefore part of certificate operations.

## Expiration and recovery strategy

Plan before enabling pinning for expired certificates, compromised keys, an accidental pin, emergency migration, and permanently old clients. A bad pin can cause a complete outage in which the application cannot reach the service that might otherwise deliver new configuration.

Useful controls include independently usable backup pins, overlapping validity, staged mobile and server rollout, monitoring, and a defined minimum supported version. An alternative endpoint is a recovery path only if its identity and behavior were designed and protected in advance. Downloading an arbitrary replacement pin over a connection that is already untrusted defeats the purpose of pinning.

Remote configuration has the same bootstrap problem. It can select among pins or policies already authenticated by the installed application, but it cannot safely invent a new trust anchor after every pinned path has failed unless a separate authenticated recovery mechanism exists.

## Operational risks

- Pin mismatch can block all API traffic for affected versions.
- CDNs and third-party services may rotate keys outside the mobile team's control.
- Server, infrastructure, security, QA, and mobile release schedules must align.
- Old application versions remain deployed after obsolete pins should have disappeared.
- Certificate and chain changes require monitoring, alerts, owners, and a tested runbook.

Avoid pinning third-party endpoints unless the provider explicitly supports it and gives a stable operational contract. The party that can change the certificate must participate in the pin lifecycle.

## Impact on QA and debugging proxies

An interception proxy presents its own certificate chain, so a pinned production host normally rejects it even when the debug app trusts the proxy CA. Disabling pinning globally or through a user-accessible switch makes production behavior ambiguous.

If traffic inspection is required, use an explicitly controlled debug variant with separate client construction or trust configuration. Release variants must preserve production pinning. Automated checks should prove that debug exceptions, proxy CAs, and bypass configuration are absent from release artifacts.

When declarative Network Security Configuration pins are used, Android can bypass those pins for chains trusted through `debug-overrides`. This does not automatically bypass a separately configured OkHttp `CertificatePinner`.

## Testing pinning

| Scenario | Expected result | Typical level |
| --- | --- | --- |
| Valid primary pin | Connection succeeds | Integration |
| Valid backup pin | Connection succeeds | Integration or staging |
| Trusted chain with unpinned key | Pinning failure | Integration |
| Invalid certificate chain | TLS failure before pin check | Integration |
| Hostname mismatch | TLS failure before pin check | Integration |
| Old and new pins during rotation | Both planned deployments work | Staging |
| Release variant | Production pin policy is present | Build/integration |
| Debug proxy | Works only under the intended debug policy | Manual/integration |
| Supported old app version | Behavior matches the rotation plan | Staging/device matrix |

Pure unit tests can verify configuration selection and host-pattern logic. Real TLS, chain-building, proxy, and rotation behavior need integration or staging infrastructure.

## When pinning is justified

Pinning may be justified for high-value financial or identity operations, an explicit regulatory or enterprise requirement, or a concrete threat model where reducing CA trust materially helps. The strongest candidates use controlled first-party infrastructure and already have mature key management, monitoring, staged rollout, and emergency recovery processes.

The decision should name the attacker, protected asset, acceptable availability risk, and teams that own future rotation. "More security" is not a sufficient requirement.

## When standard TLS is sufficient

Standard platform TLS is often preferable for ordinary application risk, third-party or CDN-managed infrastructure, teams that cannot coordinate certificate rotation, and products where the outage risk exceeds the additional trust reduction. Correct chain validation, hostname verification, cleartext blocking, dependency maintenance, and backend authorization remain a strong baseline.

> Pinning is not only a client-side code decision. It is a long-term operational commitment shared by mobile, backend, infrastructure, security, and QA teams.

## Related topics

- [HTTPS, TLS and Certificates](https-tls-certificates.md)
- [Android Security Basics](index.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
- [Network Inspection](../tools/network-inspection.md)
