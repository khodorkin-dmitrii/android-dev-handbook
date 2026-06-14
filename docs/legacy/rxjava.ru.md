# RxJava

RxJava - legacy reactive library для работы с asynchronous streams, events и composition операторов. В modern Android многие сценарии переехали на Coroutines и Flow, но RxJava всё ещё часто встречается в production-коде.

## Operators

### `.map()` vs `.flatMap()`

`.map()` превращает каждый элемент stream в другой элемент.

```kotlin
usersObservable
    .map { user -> user.name }
```

`.flatMap()` превращает каждый элемент stream в новый `Observable` / `Single` / другой reactive source и затем объединяет emissions во внешний stream.

```kotlin
userIdsObservable
    .flatMap { id -> api.getUser(id).toObservable() }
```

Главная разница: `map` делает синхронное преобразование value -> value, а `flatMap` раскрывает value -> stream и подходит для async-зависимых операций.

Ссылка: [RxJava Operator Map vs FlatMap](https://medium.com/mindorks/rxjava-operator-map-vs-flatmap-427c09678784)

**Коротко:** `map` преобразует элемент, `flatMap` запускает новый reactive source для элемента и объединяет результаты.

### `.flatMap()`, `concatMap()`, `switchMap()`

`flatMap()` не гарантирует порядок emissions от внутренних streams. После создания inner `Observable` они выполняются независимо, и результаты могут прийти в любом порядке.

`concatMap()` сохраняет порядок обработки в соответствии с порядком исходных элементов. Но inner streams выполняются последовательно, поэтому общий pipeline может стать медленнее.

`concatMapEager()` запускает inner streams параллельно, но отдаёт результаты в исходном порядке. Это может требовать больше памяти, потому что результаты нужно буферизовать.

`switchMap()` при появлении нового inner stream отписывается от предыдущего. Типичный пример - поисковая строка: если пользователь ввёл новый запрос, результат старого запроса уже не нужен.

Ссылки:

- [RxJava FlatMap, SwitchMap and ConcatMap](https://medium.com/appunite-edu-collection/rxjava-flatmap-switchmap-and-concatmap-differences-examples-6d1f3ff88ee0)
- [flatMap vs concatMap vs concatMapEager](https://www.nurkiewicz.com/2017/08/flatmap-vs-concatmap-vs-concatmapeager.html)

**Коротко:** `flatMap` даёт concurrency без гарантии порядка, `concatMap` сохраняет порядок последовательно, `switchMap` оставляет только последний актуальный inner stream.

### Отличие `observeOn()` и `subscribeOn()`

`subscribeOn()` определяет scheduler, на котором будет выполнена подписка и upstream work ближе к source. Обычно неважно, где в chain поставить `subscribeOn()`: если их несколько, обычно сработает тот, который ближе к созданию source.

`observeOn()` переключает scheduler для downstream-операторов, которые находятся ниже по цепочке, до следующего `observeOn()`.

```kotlin
api.loadUser()
    .subscribeOn(Schedulers.io())
    .map { it.toUiModel() }
    .observeOn(AndroidSchedulers.mainThread())
    .subscribe { uiModel -> render(uiModel) }
```

В Android типичный pattern: network/database work выполняется на `Schedulers.io()`, а UI update - на `AndroidSchedulers.mainThread()`.

Ссылка: [RxJava subscribeOn vs observeOn](https://medium.com/upday-devs/rxjava-subscribeon-vs-observeon-9af518ded53a)

**Коротко:** `subscribeOn()` влияет на upstream subscription/source work, `observeOn()` переключает scheduler для дальнейшей обработки ниже по chain.

### ops: `from`, `just` - для чего и в чем отличия

`just()` создаёт source, который emit-ит переданный аргумент как есть. Если передано несколько аргументов, они будут emit-иться по очереди, но количество аргументов ограничено overload-ами.

```kotlin
Observable.just("A", "B", "C")
```

`from...()` создаёт source из другого типа данных: `Iterable`, array, `Callable`, `Future`, `Publisher` и т.д. Например, `fromIterable()` emit-ит элементы коллекции по одному.

```kotlin
Observable.fromIterable(listOf("A", "B", "C"))
```

Если передать список в `just(list)`, downstream получит один элемент - сам список. Если использовать `fromIterable(list)`, downstream получит каждый элемент списка отдельно.

Ссылки:

- [Just](http://reactivex.io/documentation/operators/just.html)
- [From](http://reactivex.io/documentation/operators/from.html)

**Коротко:** `just()` emit-ит аргументы как values, `fromIterable()` / `from...()` раскрывает container/source в emissions.

### ops: `doOn...Next`, `...Error`

`doOn...` operators позволяют выполнить side effect на разных событиях lifecycle reactive chain, не меняя сами emissions.

Частые варианты:

- `doOnNext()` - выполнить действие перед передачей `onNext` downstream;
- `doAfterNext()` - выполнить действие после передачи `onNext`;
- `doOnComplete()` - выполнить действие при успешном завершении;
- `doOnError()` - выполнить действие при ошибке;
- `doOnTerminate()` - выполнить действие перед завершением, независимо от success/error;
- `doAfterTerminate()` - выполнить действие после завершения.

```kotlin
repository.observeItems()
    .doOnNext { items -> logger.log("items=${items.size}") }
    .doOnError { error -> logger.log(error) }
    .subscribe()
```

**Важно:** `doOn...` хорошо подходит для logging, metrics, debugging и lightweight side effects. Business logic лучше не прятать в side-effect operators.

Ссылка: [Do operator documentation](http://reactivex.io/documentation/operators/do.html)

**Коротко:** `doOn...` operators добавляют side effects на lifecycle events stream, не преобразуя данные.

## Types and Backpressure

### `Observable` vs `Flowable`

`Observable` не имеет встроенной backpressure-стратегии. Если producer emit-ит элементы быстрее, чем consumer успевает их обрабатывать, возможны проблемы с памятью или `MissingBackpressureException` в местах, где backpressure ожидается.

`Flowable` предназначен для streams, где backpressure важен: быстрые источники событий, большие объёмы данных, sensors, streams из producer-а, который может быть быстрее consumer-а.

Backpressure - ситуация, когда элементы создаются быстрее, чем downstream может их обработать.

Ссылка: [RxJava 2 Flowable](https://www.baeldung.com/rxjava-2-flowable)

**Коротко:** `Observable` подходит для обычных streams без backpressure, `Flowable` нужен там, где producer может перегрузить consumer.

### `Flowable` - backpressure strategies

`Flowable` поддерживает разные стратегии работы с backpressure.

`Buffer` - события, которые не успевают обрабатываться, попадают в буфер. Подходит, когда нужно обязательно обработать все события, но опасен для бесконечных или слишком быстрых streams.

`Drop` - события, которые не успевают обрабатываться, отбрасываются. Пример - sensor data, где слишком высокая частота не нужна.

`Latest` - сохраняется только последнее актуальное событие из тех, которые downstream не успевает обработать.

`Error` - при backpressure выбрасывается `MissingBackpressureException`. Подходит, когда backpressure не ожидается и должен считаться ошибкой.

`Missing` - стратегия не задаётся на source-level, и backpressure должен быть обработан дальше в chain.

Ссылка: [RxJava 2 Flowable](https://www.baeldung.com/rxjava-2-flowable)

**Коротко:** backpressure strategy выбирают по смыслу stream: обработать всё, отбросить лишнее, взять последнее или явно упасть с ошибкой.

### `Single`, `Completable`, `Maybe`

`Single<T>` emit-ит ровно один item или ошибку. Хороший пример - загрузить объект по id.

`Maybe<T>` emit-ит один item, ошибку или просто завершается без значения. Подходит для поиска, где результат может отсутствовать.

`Completable` не emit-ит value: он либо завершается успешно, либо ошибкой. Подходит для операций вроде update/delete/save, где важен только факт завершения.

```kotlin
fun loadUser(id: String): Single<User>
fun findCachedUser(id: String): Maybe<User>
fun updateUser(user: User): Completable
```

Ссылка: [RxJava Single, Maybe and Completable](https://android.jlelse.eu/rxjava-single-maybe-and-completable-8686db42bac8)

**Коротко:** `Single` - один value, `Maybe` - value или empty, `Completable` - только success/error без value.

## More Operators

### ops: `defer`, `debounce`

`defer()` создаёт source только в момент подписки. Для каждого subscriber создаётся новый "свежий" source.

```kotlin
val source = Observable.defer {
    Observable.just(System.currentTimeMillis())
}
```

`debounce()` ждёт заданный промежуток после emission. Если за это время приходит новое значение, предыдущее отбрасывается, таймер начинается заново. Когда пауза выдержана, последнее значение проходит дальше.

Типичный сценарий - поисковая строка:

```kotlin
queryChanges
    .debounce(300, TimeUnit.MILLISECONDS)
    .switchMap { query -> api.search(query).toObservable() }
```

**Коротко:** `defer` откладывает создание source до подписки, `debounce` пропускает только значение после паузы в emissions.

### ops: `groupBy`, `combineLatest`, `withLatestFrom`, `switchOnNext`

`groupBy()` превращает stream элементов в stream grouped streams. Каждый inner stream содержит подмножество исходных элементов по key.

`combineLatest()` emit-ит результат, когда любой из source streams emit-ит новое значение, используя последние значения остальных sources. Начинает работать, когда каждый source emit-нул хотя бы одно значение.

`withLatestFrom()` похож на `combineLatest`, но emission инициирует только основной source. Значение второго source берётся как latest context.

`switchOnNext()` работает со stream of streams: подписывается на последний inner `Observable` и отписывается от предыдущего. В результате downstream получает emissions только из актуального inner stream.

```kotlin
Observable.combineLatest(user, settings) { userValue, settingsValue ->
    UiModel(userValue, settingsValue)
}
```

**Коротко:** `groupBy` группирует stream, `combineLatest` реагирует на любой source, `withLatestFrom` добавляет latest context, `switchOnNext` переключается на последний inner stream.

### ops: `merge`, `concat`, `zip`

`merge()` объединяет emissions из нескольких streams в один downstream stream без ожидания порядка между sources.

`concat()` тоже объединяет streams, но выполняет их последовательно: сначала все emissions первого source до completion, затем второго и т.д.

`zip()` комбинирует emissions попарно: первый элемент первого stream с первым элементом второго, второй со вторым и т.д.

```kotlin
Observable.zip(userSingle.toObservable(), settingsSingle.toObservable()) { user, settings ->
    UiModel(user, settings)
}
```

Ссылки:

- [defer](http://reactivex.io/documentation/operators/defer.html)
- [groupBy](http://reactivex.io/documentation/operators/groupby.html)
- [debounce](http://reactivex.io/documentation/operators/debounce.html)
- [combineLatest](http://reactivex.io/documentation/operators/combinelatest.html)
- [merge](http://reactivex.io/documentation/operators/merge.html)
- [concat](http://reactivex.io/documentation/operators/concat.html)
- [zip](http://reactivex.io/documentation/operators/zip.html)

**Коротко:** `merge` смешивает emissions, `concat` сохраняет последовательное выполнение sources, `zip` объединяет emissions попарно.
