# lateinit vs lazy in Kotlin

Kotlin normally requires a property to be initialized when it is declared or during object construction. `lateinit` and `lazy` cover two different cases where the value becomes available later.

## `lateinit var`

`lateinit` postpones the assignment of a mutable property. The developer is responsible for assigning it before the first read.

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
    }
}
```

Reading an uninitialized property throws `UninitializedPropertyAccessException`. A `lateinit` property:

- must be a `var`;
- must have a non-null reference type, so primitive types such as `Int` are not supported;
- may be top-level, local, or declared in a class body, but cannot be declared in a primary constructor or have a custom getter or setter;
- can be assigned again after initialization.

`lateinit` does not add synchronization or visibility guarantees between threads. If several threads access the property, their coordination must be handled separately.

For diagnostics, initialization can be checked through a property reference:

```kotlin
if (this::binding.isInitialized) {
    // binding has been assigned
}
```

`isInitialized` should not be the default way to organize runtime control flow. Its use is limited to an accessible backing field: a property declared in the same class, an outer class, or as a top-level property in the same file. Usually it is clearer to design the initialization order explicitly.

## `val by lazy`

`lazy()` returns `Lazy<T>`, which can be used as a property delegate. Its initializer runs on the first read, and the successfully computed value is cached for subsequent reads.

```kotlin
private val parser by lazy {
    JsonParser(configuration)
}
```

If the initializer throws an exception, no value is cached. The next access tries to run the initializer again.

A lazy property does not reset automatically. Its lifetime follows the object that owns the delegate, so it is suitable only when the computed value should live that long.

## Thread-safety modes

The default mode is `LazyThreadSafetyMode.SYNCHRONIZED`.

- `SYNCHRONIZED` uses a lock so only one thread initializes the value and the result is visible to all threads.
- `PUBLICATION` allows the initializer to run several times concurrently, but only one computed value is published and observed by all threads. The initializer should therefore be safe to execute more than once.
- `NONE` uses no synchronization and provides no thread-safety guarantees. Use it only when access is guaranteed to stay on one thread.

```kotlin
private val cache by lazy(LazyThreadSafetyMode.NONE) {
    ScreenCache()
}
```

## Comparison

| Property | `lateinit var` | `val by lazy` |
| --- | --- | --- |
| Who starts initialization | Developer | First read |
| Mutability | Can be assigned repeatedly | Read-only property |
| Read before initialization | Throws an exception | Runs the initializer |
| Type restrictions | Non-null reference type | Supports nullable and primitive values |
| Thread-safety | Not provided | Configured by mode |
| Automatic reset | No | No |

Use `lateinit` when an external lifecycle or framework callback supplies a mutable value later. Use `lazy` when the value can be computed from available inputs on first access and should then remain unchanged.

## Android lifecycle examples

An `Activity` binding may be stored in `lateinit var` when it is assigned in `onCreate()` before any use. The property and the `Activity` instance share the same lifecycle.

A Fragment is different because its View can be destroyed while the Fragment object remains alive. A binding cached with ordinary `lazy` cannot be reset, and a `lateinit` binding can retain a destroyed View or expose stale state. Prefer a nullable backing property tied to the View lifecycle:

```kotlin
private var _binding: FragmentProfileBinding? = null
private val binding get() = requireNotNull(_binding)

override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
    _binding = FragmentProfileBinding.bind(view)
}

override fun onDestroyView() {
    _binding = null
    super.onDestroyView()
}
```

See [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md) for the distinction between the Fragment and View lifecycles.

`lazy` fits values whose lifetime matches their owner, for example an Android system service used by an `Activity`:

```kotlin
private val notificationManager by lazy {
    getSystemService(NotificationManager::class.java)
}
```

Dependencies are usually better supplied through constructor injection where the framework and architecture allow it. `lateinit` field injection should not replace an explicit dependency contract merely to avoid constructor parameters.

## See also

- [`object` declarations and companion objects](classes-and-types.md)
- [ViewBinding vs DataBinding](../android/view-system-xml-ui.md#viewbinding-vs-databinding)
