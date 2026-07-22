# OAuth 2.0, PKCE and Token Management

Native Android applications are public clients: their binaries and runtime behavior can be inspected, so an embedded static client secret cannot be confidential. A robust session therefore uses a flow designed for public clients, sends the user to a trusted external browser, treats tokens as scoped and revocable credentials, and coordinates refresh as an explicit state transition.

## OAuth 2.0 and OpenID Connect

OAuth 2.0 is a framework for delegated authorization. It lets a client obtain limited access to a protected resource without collecting the resource owner's password. OAuth itself is not a login protocol.

OpenID Connect (OIDC) adds an identity layer on top of OAuth 2.0. Applications commonly use OIDC to sign a user in and OAuth access tokens to authorize API calls:

- An **access token** authorizes calls to a particular resource server for an audience and scope.
- An **ID token** communicates an authentication event and identity claims to the client.
- A **refresh token** can obtain a new access token according to provider policy.

These values are not interchangeable. An ID token is not a general API credential, and an API must not accept a token issued for another audience.

## Native application authorization model

An installed Android application cannot keep a shared static secret from the device owner. A value packaged in the APK, resources, native code, or remote configuration available to every installation is a public client credential, even if obfuscated.

Native applications should use registered redirect URIs and flows intended for public clients. Redirect handling must prove that the response belongs to the initiating application as strongly as the platform and provider allow, using claimed HTTPS redirects or carefully registered custom schemes. The authorization service must validate the exact redirect URI.

A backend-for-frontend or another confidential server component is a different trust environment because it can protect service credentials and authenticate server-to-server connections. Adding such a backend changes token ownership and API architecture; it does not make an APK-held secret confidential.

## Authorization Code Flow with PKCE

Proof Key for Code Exchange binds an authorization request to the client instance that started it:

1. Generate a high-entropy, one-time `code_verifier`.
2. Derive `code_challenge = BASE64URL(SHA256(code_verifier))`.
3. Open the authorization request with the challenge, `S256`, and a fresh `state`.
4. The user authenticates and grants access at the authorization service.
5. The app receives a short-lived, one-time authorization code through a validated redirect.
6. The app exchanges the code and original verifier for tokens.
7. The authorization server verifies that the verifier produces the stored challenge.

An intercepted code is not useful without the verifier. Use `S256`, a cryptographically random verifier for every attempt, and retain it only for the active authorization transaction. `state` correlates request and response and helps prevent cross-request or CSRF-style substitution. In OIDC, a fresh `nonce` binds the authentication request to the ID token and must be validated.

PKCE does not validate redirect ownership or replace `state`, `nonce`, TLS, or backend authorization. Prefer a mature standards-compliant OAuth/OIDC library such as AppAuth when it fits the provider instead of manually assembling protocol requests and token validation.

## Browser-based authentication

Native authorization should normally open the system browser or a browser-backed surface such as Custom Tabs. The application does not directly receive the user's password, the user can recognize the authorization origin, and the flow can reuse provider sessions, password managers, security keys, passkeys, and browser security controls.

A standards-compliant client library also handles discovery, redirect matching, PKCE encoding, and protocol error details more reliably than custom URI construction. The application still owns lifecycle state, cancellation, account selection, and safe persistence after the token response.

## Why embedded WebView login is usually inappropriate

For authentication with an external identity provider, a WebView is an embedded user agent controlled by the application. The host app can inspect page content and credential input, while the user cannot reliably verify the real origin. Shared provider sessions, password managers, security keys, and passkeys may not work as expected, and providers may block embedded authorization.

This does not mean every WebView page is inherently insecure. The warning is specifically about using an embedded surface to collect credentials or run third-party authorization. Use the provider's supported external-browser flow unless an explicitly reviewed first-party authentication architecture requires something else.

## Access tokens

Most access tokens are bearer credentials: possession is sufficient to use them. Send a token only to the intended HTTPS origin and API audience, in the `Authorization` header, never in a URL. URLs commonly reach histories, analytics, referrers, screenshots, and infrastructure logs.

Keep scopes narrow and lifetimes short enough for the product risk. Do not send one provider's token to unrelated hosts or assume a token is valid merely because it has not reached a locally decoded expiration time. Network logging, crash reports, analytics, and debug tools must redact authorization headers and token responses.

## Refresh tokens

Refresh tokens usually live longer and have greater impact than access tokens. A provider may rotate them on every use, detect reuse of an old token, revoke a token family, bind them to a client or device signal, or decline to issue them at all.

The client must atomically adopt every new token set, including a replacement refresh token. Refresh denial is a normal terminal session state, not an exceptional condition to retry forever. Provider policy defines expiration, inactivity windows, revocation, and whether an old refresh token remains valid.

## Token expiration

Two strategies are useful:

- **Proactive refresh:** refresh shortly before a known expiry to reduce failed foreground calls.
- **Reactive refresh:** respond to an authentication failure when the server rejects the credential.

A balanced design can use both. Account for clock skew and avoid refreshing on every request. The server remains authoritative, and a `401` does not prove that the token merely expired: it may be revoked, malformed, intended for another audience, or associated with an invalid session.

## Secure token storage

An access token can remain memory-only when re-authentication after process death is acceptable. A refresh token normally needs more deliberate persistence if the product promises session restoration or background work. Use Keystore-backed encrypted persistence with a defined backup, invalidation, migration, and recovery policy rather than plain preferences.

Encryption reduces casual extraction and offline inspection. It cannot hide a token after it is loaded into a compromised process. Keep token sets isolated per account, replace access and refresh tokens atomically, and clear the entire selected session on logout. Storage architecture is covered in [Android Keystore and Secure Storage](keystore-secure-storage.md).

## Adding authorization to requests

An application interceptor can add the latest token to calls for the exact API HTTPS origin. It should not cache one token forever or attach credentials to redirects and unrelated origins:

```kotlin
interface TokenStore {
    fun current(): TokenSet?
    fun replace(tokens: TokenSet)
    fun clear()
}

data class TokenSet(
    val accessToken: String,
    val refreshToken: String?,
)

private fun HttpUrl.hasSameOrigin(other: HttpUrl): Boolean =
    scheme == other.scheme &&
        host == other.host &&
        port == other.port

class AccessTokenInterceptor(
    private val apiOrigin: HttpUrl,
    private val tokenStore: TokenStore,
) : Interceptor {
    init {
        require(apiOrigin.isHttps) { "API origin must use HTTPS" }
    }

    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request()
        if (!request.url.hasSameOrigin(apiOrigin) || request.header("Authorization") != null) {
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

Bearer tokens should be scoped to the intended HTTPS origin - scheme, host, and port - rather than merely a matching hostname. This check is required even when application-wide cleartext policy is also configured.

`TokenStore.current()` should normally return a fast, thread-safe in-memory snapshot. Encrypted persistent storage should hydrate and atomically update that snapshot rather than decrypting data from disk for every HTTP request. Logging interceptors must redact `Authorization`. Refresh orchestration belongs outside this interceptor so ordinary requests do not start independent refresh calls.

## Refreshing tokens

Refresh is a session state transition:

1. Read one internally consistent token set.
2. Exchange the refresh token using a dedicated client that cannot trigger the same authenticator recursively.
3. Classify the result as success, rejected credentials, or transient failure.
4. Atomically replace both tokens on success.
5. Clear or invalidate the session when the provider definitively rejects refresh.
6. Keep the session for a transient network failure and surface a retryable result.

Persisting a new access token while retaining an obsolete rotated refresh token creates a broken session. Store the complete set as one versioned record or transaction.

## Concurrent requests and single-flight refresh

Several parallel calls can receive `401` for the same token. If each refreshes independently, refresh-token rotation may cause the requests to invalidate one another, publish inconsistent token sets, create a refresh storm, or force logout.

A single-flight coordinator allows one refresh at a time. After entering the critical section, it checks whether another request already replaced the failed token. The example uses a JVM monitor because OkHttp's `Authenticator` is synchronous and runs off the main thread:

```kotlin
sealed interface RefreshOutcome {
    data class Refreshed(val tokens: TokenSet) : RefreshOutcome
    data object SessionRejected : RefreshOutcome
    data object TemporarilyUnavailable : RefreshOutcome
    data object NotRefreshable : RefreshOutcome
}

interface AuthApi {
    fun refresh(refreshToken: String): RefreshOutcome
}

class TokenRefreshCoordinator(
    private val tokenStore: TokenStore,
    private val authApi: AuthApi,
) {
    private val lock = Any()

    fun refreshAfter(failedAccessToken: String): RefreshOutcome {
        return synchronized(lock) {
            val current = tokenStore.current()
                ?: return@synchronized RefreshOutcome.NotRefreshable

            if (current.accessToken != failedAccessToken) {
                return@synchronized RefreshOutcome.Refreshed(current)
            }

            val refreshToken = current.refreshToken
                ?: return@synchronized RefreshOutcome.NotRefreshable

            when (val result = authApi.refresh(refreshToken)) {
                is RefreshOutcome.Refreshed -> {
                    tokenStore.replace(result.tokens)
                    result
                }
                RefreshOutcome.SessionRejected -> {
                    tokenStore.clear()
                    result
                }
                RefreshOutcome.TemporarilyUnavailable,
                RefreshOutcome.NotRefreshable -> result
            }
        }
    }
}
```

`AuthApi` must use a client without this authenticator to avoid recursion. The explicit outcome preserves the distinction between a rejected session, a temporary failure that must not clear persisted credentials, and a session that has no refresh token. The monitor-based example intentionally blocks waiting callers while one refresh is in progress. A production implementation may represent the in-flight refresh as a shared result or future so callers wait for the same operation without coupling unrelated session work to the same monitor. It should also support cancellation and timeouts and make persistence atomic.

## OkHttp interceptor vs authenticator

An **interceptor** modifies outgoing requests and is a good place to attach the current authorization header for a known HTTPS origin. It should not blindly refresh and replay calls.

An **authenticator** reacts to server authentication challenges such as `401` and may build a follow-up request. OkHttp can invoke it concurrently, so it needs loop prevention and the shared refresh coordinator.

```kotlin
class AccessTokenAuthenticator(
    private val apiOrigin: HttpUrl,
    private val tokenStore: TokenStore,
    private val refreshCoordinator: TokenRefreshCoordinator,
) : Authenticator {
    init {
        require(apiOrigin.isHttps) { "API origin must use HTTPS" }
    }

    override fun authenticate(route: Route?, response: Response): Request? {
        if (!response.request.url.hasSameOrigin(apiOrigin) || responseCount(response) >= 2) {
            return null
        }

        val authorization = response.request.header("Authorization") ?: return null
        val failedToken = authorization.removePrefix("Bearer ")
        if (failedToken == authorization) return null

        val tokens = when (val outcome = refreshCoordinator.refreshAfter(failedToken)) {
            is RefreshOutcome.Refreshed -> outcome.tokens
            RefreshOutcome.SessionRejected,
            RefreshOutcome.TemporarilyUnavailable,
            RefreshOutcome.NotRefreshable -> return null
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

This abbreviated sample retries an authenticated request at most once, compares the rejected token with the latest snapshot before refreshing, reuses a token already refreshed by another call, and returns `null` when it cannot satisfy the challenge. A session without a refresh token is non-refreshable. Rejected credentials clear the session, while transient failures preserve it. The sample omits provider-specific errors, non-repeatable request bodies, cancellation, metrics, account switching, persistence implementation, and UI session events. Review whether replaying each API operation is safe.

## Handling `401 Unauthorized`

A finite decision flow prevents loops:

1. Verify that the failed request actually used an access token for the expected HTTPS origin.
2. Stop if the request has already been retried.
3. Reuse a newer token if another request already refreshed the session.
4. Refresh only when a valid refreshable session exists.
5. Retry the original operation once with the new token.
6. End the session when refresh credentials are rejected.
7. Surface a transient network failure differently from invalid credentials.

`401` can mean a missing, expired, revoked, malformed, incorrectly signed, or wrong-audience token, or a provider-specific invalid session. Insufficient permission is commonly `403`, but the backend contract is authoritative. Do not refresh forever or convert every authorization failure into logout without classifying it.

## Logout and token revocation

Logout has several related but distinct parts:

- stop attaching the selected token set to new requests;
- atomically clear persisted and in-memory session state;
- cancel or isolate in-flight authenticated work and account-scoped caches;
- revoke refresh or access tokens at the authorization service when supported;
- optionally invoke the provider's OIDC end-session behavior.

Local app logout, token revocation, and identity-provider browser logout are not the same operation. Clearing application tokens does not necessarily clear the user's system-browser provider session. Define the expected UX and privacy behavior explicitly, especially on shared devices and with multiple accounts.

## Process death and session restoration

Persist only the token state required by product behavior. On restart, decrypt one versioned record, verify that access and refresh tokens belong to one account and session, and refresh or require authentication if the state is incomplete or rejected.

Authorization codes, `state`, `nonce`, and PKCE verifiers are temporary transaction data. Retain them only while a specific flow can complete, bind the redirect to that flow, and clear abandoned or consumed state. Multiple-account applications need account-scoped token records and an atomic selected-account transition.

## JWT limitations

JWT is a token format, not an authorization architecture, and not every OAuth token is a JWT. Base64url-decoding a JWT only parses readable claims; it does not validate signature, issuer, audience, expiry, nonce, or authorization.

The backend must validate access tokens and enforce resource permissions. The Android client must not grant security-sensitive capability based on an unverified decoded claim. Signed JWTs are normally encoded, not encrypted, so sensitive plaintext does not belong in claims merely because the token has a signature.

JWT does not automatically solve revocation or logout. For ID tokens, use a standards-compliant OIDC library and provider metadata rather than ad hoc parsing or signature logic.

## Common implementation mistakes

- Embedding a permanent client secret in the APK.
- Collecting an external provider's password inside the application or WebView.
- Omitting PKCE, reusing a verifier, or using weak randomness.
- Failing to validate the exact redirect, `state`, or OIDC `nonce`.
- Storing tokens in plain preferences or logging headers and token responses.
- Sending a bearer token to an unrelated host or placing it in a URL.
- Refreshing on every `401` without classifying the failure.
- Starting parallel refreshes with a rotating refresh token.
- Creating an authenticator loop or replaying a request without a bound.
- Updating access and refresh tokens non-atomically.
- Retaining tokens, caches, or in-flight work after logout or account switch.
- Trusting decoded JWT claims without standards-compliant validation.

## Practical architecture summary

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

The core principles are stable: treat the app as a public client, embed no confidential client secret, use Authorization Code Flow with PKCE in an external browser, keep access tokens short-lived, protect refresh-token persistence, coordinate one bounded refresh, and leave authoritative authorization to the backend.

## Related topics

- [Android Keystore and Secure Storage](keystore-secure-storage.md)
- [Android Security Basics](index.md)
- [HTTPS, TLS and Certificates](https-tls-certificates.md)
- [Retrofit / OkHttp](../networking/retrofit-okhttp.md)
