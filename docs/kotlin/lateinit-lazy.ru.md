# lateinit и lazy в Kotlin

Обычно Kotlin требует инициализировать property при объявлении или во время создания объекта. `lateinit` и `lazy` решают два разных случая, когда значение становится доступно позже.

## `lateinit var`

`lateinit` откладывает присваивание mutable property. Разработчик отвечает за то, чтобы присвоить значение до первого чтения.

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

Чтение неинициализированного property приводит к `UninitializedPropertyAccessException`. Property с `lateinit`:

- должен быть `var`;
- должен иметь non-null reference type, поэтому primitive types вроде `Int` не поддерживаются;
- может быть top-level, local или объявленным в body класса, но не в primary constructor, и не может иметь custom getter либо setter;
- допускает повторное присваивание после инициализации.

`lateinit` не добавляет синхронизацию или гарантии видимости между потоками. Если к property обращаются несколько потоков, их координацию нужно реализовать отдельно.

Для диагностики состояние инициализации можно проверить через property reference:

```kotlin
if (this::binding.isInitialized) {
    // binding уже присвоено значение
}
```

`isInitialized` не стоит использовать как основной способ организации runtime control flow. Проверка ограничена доступным backing field: property должен быть объявлен в том же классе, outer class или как top-level property в том же файле. Обычно понятнее явно спроектировать порядок инициализации.

## `val by lazy`

`lazy()` возвращает `Lazy<T>`, который можно использовать как property delegate. Initializer запускается при первом чтении, а успешно вычисленное значение кэшируется для последующих обращений.

```kotlin
private val parser by lazy {
    JsonParser(configuration)
}
```

Если initializer выбросил exception, значение не кэшируется. При следующем обращении initializer будет запущен снова.

Lazy property не сбрасывается автоматически. Его lifetime совпадает с lifetime объекта, которому принадлежит delegate, поэтому такой подход подходит только тогда, когда вычисленное значение должно жить столько же.

## Режимы потокобезопасности

По умолчанию используется `LazyThreadSafetyMode.SYNCHRONIZED`.

- `SYNCHRONIZED` использует lock: значение инициализирует только один поток, а результат виден всем потокам.
- `PUBLICATION` допускает несколько конкурентных запусков initializer, но опубликовано и доступно всем потокам будет только одно вычисленное значение. Поэтому initializer должен допускать повторное выполнение.
- `NONE` не использует синхронизацию и не даёт гарантий потокобезопасности. Этот режим подходит только при гарантированно однопоточном доступе.

```kotlin
private val cache by lazy(LazyThreadSafetyMode.NONE) {
    ScreenCache()
}
```

## Сравнение

| Свойство | `lateinit var` | `val by lazy` |
| --- | --- | --- |
| Кто запускает инициализацию | Разработчик | Первое чтение |
| Mutability | Повторное присваивание возможно | Только чтение |
| Чтение до инициализации | Выбрасывает exception | Запускает initializer |
| Ограничения типа | Non-null reference type | Поддерживает nullable и primitive values |
| Потокобезопасность | Не предоставляется | Настраивается режимом |
| Автоматический reset | Нет | Нет |

Используйте `lateinit`, когда mutable value позже предоставляет внешний lifecycle или framework callback. Используйте `lazy`, когда значение можно вычислить из доступных данных при первом обращении, после чего оно не должно меняться.

## Android lifecycle: примеры

Binding в `Activity` можно хранить в `lateinit var`, если присвоить его в `onCreate()` до первого использования. Property и instance `Activity` имеют общий lifecycle.

С Fragment ситуация отличается: его View может быть уничтожена, пока Fragment object продолжает жить. Binding, сохранённый через обычный `lazy`, нельзя сбросить, а `lateinit` binding может удерживать уничтоженную View или предоставлять устаревшее состояние. Лучше использовать nullable backing property, привязанный к View lifecycle:

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

Различие между lifecycle Fragment и его View подробнее разобрано в статье [Activity, Fragment & Lifecycle](../android/activity-fragment-lifecycle.md).

`lazy` подходит для значений, lifetime которых совпадает с lifetime владельца, например для Android system service в `Activity`:

```kotlin
private val notificationManager by lazy {
    getSystemService(NotificationManager::class.java)
}
```

Там, где framework и архитектура это позволяют, зависимости обычно лучше передавать через constructor injection. `lateinit` field injection не должен заменять явный dependency contract только ради отказа от параметров конструктора.

## См. также

- [`object` declarations и companion objects](classes-and-types.md)
- [ViewBinding vs DataBinding](../android/view-system-xml-ui.md#viewbinding-vs-databinding)
