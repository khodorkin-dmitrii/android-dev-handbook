# Memory & Runtime Basics

![Stack vs Heap](../assets/images/fundamentals/stack-vs-heap.png)

Core memory and runtime concepts help explain memory leaks, object lifetime, GC behavior and Java/Kotlin code behavior on Android.

## Memory and GC

### Stack vs Heap

Stack is a memory area for the call stack, local variables, call parameters and return addresses. It is fast and released automatically when a function exits.

Heap is a memory area for objects that can live longer than one function call. The Garbage Collector is responsible for releasing them.

In Java/Kotlin, an object is usually created in the heap, while a local variable can store a reference to that object.

Each thread has its own stack. If it overflows, `StackOverflowError` occurs. Heap is shared for objects, and when memory is insufficient, `OutOfMemoryError` is possible.

### Garbage Collection roots

GC roots are starting points from which the Garbage Collector determines reachable objects.

GC roots include active thread stacks, static fields, JNI references, system class loader references and objects held by a monitor lock. If an object is reachable from a root, it is considered alive and will not be collected.

Memory leak happens when an object is no longer needed logically, but is still reachable through some chain of references.

### Strong / Soft / Weak / Phantom references

Strong reference is a regular reference. While an object is reachable through a strong reference, GC will not collect it.

Weak reference does not keep an object from garbage collection. It is useful for caches, listeners or situations where an object's lifetime must not be extended.

Soft reference can be kept longer and cleared when memory is low, but in modern Android explicit cache policies are usually better.

Phantom reference is a reference for low-level tracking of the moment when an object becomes unreachable. Together with `ReferenceQueue`, it allows resource cleanup without `finalize()`. It is rare in regular Android development.
