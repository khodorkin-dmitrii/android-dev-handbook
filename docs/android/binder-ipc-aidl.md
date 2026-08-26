# Binder IPC and AIDL

Binder is Android's main interprocess communication (IPC) mechanism. AIDL adds a typed contract and generated code on top of Binder. Most application code encounters both indirectly through framework managers, but understanding the boundary helps with bound services, threading, failures and security.

## Why IPC exists on Android

Android applications normally run in separate Linux processes, commonly under different UIDs. One process cannot directly read or modify another process's memory. This isolation limits the effect of bugs and is an important security boundary, but it also means that data and operations must cross the boundary through IPC.

IPC is involved when an app talks to a component in another app process and when public framework APIs communicate with platform services. A `Service` application component is not the same thing as a platform or system service. An application `Service` also does not automatically run in another process or on a background thread; by default, it runs in its application's process and its callbacks run on that process's main thread.

## Binder mental model

A Binder interaction has a few main participants:

- the client process calls a client-side proxy;
- the proxy marshals the method identifier and supported values into a `Parcel`;
- the Binder kernel driver transports the transaction across the process boundary;
- a Binder thread in the server process receives it;
- a server-side Binder object or stub unmarshals the request and invokes the implementation;
- for a two-way call, the result or exception travels back in a reply `Parcel`.

```text
Client call
-> generated or handwritten proxy
-> request Parcel
-> Binder driver
-> server Binder thread
-> Stub / implementation
-> reply Parcel
-> client
```

Binder makes a remote operation resemble a local method call, but the resemblance is only an API convenience. The call still pays serialization, scheduling and context-switch costs. The remote process can stop, the transaction can fail, and the server can run code concurrently on Binder pool threads. Treating a Binder call as an ordinary in-memory call is a common source of UI stalls and fragile error handling.

Many Android framework APIs use Binder underneath. For example, a public manager object can act as an application-facing wrapper around a remote platform service. Normal apps should use these public SDK APIs rather than looking up hidden Binder services directly. Android still uses the Linux kernel; Binder supports its service-oriented platform architecture, but does not make Android a microkernel operating system.

## What AIDL adds

Android Interface Definition Language (AIDL) describes a typed interface that processes agree to use. Build tools generate the Binder plumbing, including a server-side `Stub` and a client-side `Proxy`. The server extends or delegates from the generated stub, while the client obtains the interface from an `IBinder`.

Arguments, return values and exceptions must be representable across the process boundary. AIDL supports primitives, selected platform types, other AIDL interfaces and declared parcelables. Custom types must have a shared definition that both sides can marshal consistently. For example:

```aidl
// DeviceStatus.aidl
package com.example.status;

parcelable DeviceStatus;
```

```aidl
// IDeviceStatusService.aidl
package com.example.status;

interface IDeviceStatusService {
    DeviceStatus getStatus();
}
```

Here `DeviceStatus` must be an AIDL-supported `Parcelable` in the same package, and the client and server must share its compatible definition. AIDL does not replace Binder and is not another transport. It generates a typed Binder interface and handles much of the repetitive marshalling and dispatch code.

## Relationship to a bound service

An application can expose a Binder endpoint through a [bound `Service`](components.md#bound-service). The server returns an `IBinder` from `Service.onBind()`. After `bindService()`, the client receives that binder asynchronously in `ServiceConnection.onServiceConnected()` and keeps it only for the lifetime of the connection.

Choose the smallest mechanism that fits the process boundary and concurrency requirements:

| Option | Appropriate use |
| --- | --- |
| Custom `Binder` | Client and service are in the same process |
| `Messenger` | Cross-process, message-based, serialized requests |
| AIDL | Typed cross-process contract, potentially multiple concurrent callers |

For the common same-process case, a custom `Binder` is simpler. `Messenger` places messages through a `Handler`, which is useful when requests should be processed serially. Direct AIDL is appropriate when a stable typed API across processes is genuinely required and the implementation is prepared for concurrent calls. It should not be the default for an ordinary application service.

## Threading, lifetime and failure model

Remote AIDL methods are synchronous by default: the caller waits until the server replies. Never perform a potentially slow remote call on the main thread. A quick-looking method can block because the server is busy, doing I/O or competing for a Binder thread. Keep payloads compact as well; Binder transactions use bounded buffers and are not a transport for large files, bitmaps or object graphs. Pass a file descriptor, URI or identifier when bulk data belongs elsewhere.

Incoming remote calls are normally dispatched on threads from the server process's Binder pool. The service implementation must therefore protect mutable state and define its concurrency model. A same-process call can be optimized into a direct call and run on the caller's thread, so local and remote deployments can expose different threading behavior. Do not rely on Binder to move work to a particular application thread.

The AIDL `oneway` modifier makes a remote call asynchronous from the caller's perspective, but the method cannot return a result. It does not remove the need for backpressure, ordering and failure design, so use it only when fire-and-forget semantics are correct.

A remote process can die at any time. Calls can throw `RemoteException`, and a bound-service client must handle `ServiceConnection.onServiceDisconnected()` or other loss-of-binding callbacks as appropriate. `IBinder.DeathRecipient` is a lower-level mechanism for observing Binder death when an advanced integration needs it. Regardless of the IPC style, pair `bindService()` with `unbindService()` according to the lifecycle that owns the connection.

## Security boundary

Exporting a bound service creates an IPC entry point that another application may try to call. Prefer an explicit `Intent` when binding to a known service and keep private services `android:exported="false"`. If other apps must connect, protect sensitive operations with suitable manifest or runtime permission checks and validate that each caller is authorized for the requested action.

Binder exposes caller identity information such as UID and PID through APIs including `Binder.getCallingUid()` and `Binder.getCallingPid()`. That identity is input to an authorization decision, not authorization by itself. Account for shared UIDs where relevant, verify packages or signatures through supported APIs when the policy requires it, and avoid trusting caller-supplied identity fields. Binder transports the request securely across the process boundary, but it does not automatically make an exported contract safe.

## App AIDL and platform AIDL

Application developers can use AIDL directly between their own processes or between cooperating apps. This is the app-level model described by the Android Developers documentation. Separately, Android framework services use many internal AIDL contracts behind public manager and SDK APIs. Hidden `ServiceManager` access and internal AOSP interfaces are implementation details, not supported public APIs for normal applications.

Stable AIDL adds compatibility tracking and versioning for platform components that can be updated separately, including some APEX and HAL boundaries. It solves a platform integration problem and imposes stricter interface rules. An application-level AIDL service normally does not need to adopt the Stable AIDL build workflow.

## See also

- [Android Components - Bound Service](components.md#bound-service)
- [Core Android System Services](android-system-services.md)
- [Performance & Memory - ANR](performance-memory.md#anr)

## Further reading

- [Binder overview - Android Open Source Project](https://source.android.com/docs/core/architecture/ipc/binder-overview)
- [AIDL overview - Android Open Source Project](https://source.android.com/docs/core/architecture/aidl)
- [Android Interface Definition Language - Android Developers](https://developer.android.com/develop/background-work/services/aidl)
- [Bound services overview - Android Developers](https://developer.android.com/develop/background-work/services/bound-services)

