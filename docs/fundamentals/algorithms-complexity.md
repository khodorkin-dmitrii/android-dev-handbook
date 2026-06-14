# Algorithms & Complexity

![Big O chart](../assets/images/fundamentals/big-o-chart.png)

Algorithmic complexity helps estimate how code scales as input data grows. This matters not only for algorithm tasks, but also for regular collections, search, sorting and list processing in an application.

## Big O

### What is Big O?

Big O is a way to describe how an algorithm's execution time or memory usage grows as input size increases.

It is not exact time in milliseconds, but a scalability estimate. For example, `O(n)` means work grows roughly linearly with input size.

Understand time complexity and space complexity separately: an algorithm can be fast in time but require a lot of additional memory.

### `O(1)`, `O(n)`, `O(log n)`, `O(n log n)`

`O(1)` is constant complexity: the operation does not depend on input size. Example: array access by index.

`O(n)` is linear complexity: the input needs to be traversed once. Example: finding an element in an unsorted array.

`O(log n)` is logarithmic complexity: at each step, the search space decreases, for example binary search.

`O(n log n)` often appears in efficient sorting algorithms such as merge sort and average-case quicksort.

A simple heuristic: one pass over a collection usually gives `O(n)`, a nested loop often gives `O(n^2)`, and halving the search space gives `O(log n)`.

## Search, Sorting and Collections

### Search complexity in a sorted array

In a sorted array, binary search can be used with `O(log n)` complexity.

The idea: compare the target value with the middle of the array and discard half of the range. This is much faster than linear search `O(n)` on large data.

But if the array is not sorted, binary search cannot be used without sorting first.

### Sorting and QuickSort

Popular sorting algorithms: bubble sort, insertion sort, merge sort, quicksort.

Quicksort runs in `O(n log n)` on average, but in the worst case can degrade to `O(n^2)` if the pivot is chosen poorly. In practice, good implementations use random pivot, median-of-three or hybrid approaches.

**Important:** for quicksort, remember both average case and worst case. Quicksort is usually fast in practice and often works in-place, but the worst case still exists.

### `ArrayList` / `LinkedList` / `HashMap` complexity

`ArrayList` gives `O(1)` access by index and usually `O(1)` append to the end, but when the internal array grows, append can become `O(n)`. Insert or remove in the middle costs `O(n)` because elements need to be shifted.

`LinkedList` gives `O(1)` insert or remove if the node is already known, but finding the required element is usually `O(n)`. In real Android/Java code, `LinkedList` often loses to `ArrayList` because of poor cache locality.

`HashMap` gives `O(1)` on average for `put()` / `get()` / `remove()`, but depends on `hashCode()`, `equals()` and key distribution. Degradation is possible in bad cases, so custom keys need correct `equals()` / `hashCode()` implementations.
