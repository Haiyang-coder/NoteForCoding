[TOC]

#解决可见性和顺序性问题
可见性问题来自有cpu的缓存,顺序性问题来自于编译器的优化.缓存和编译优化不能一刀切的禁用,所以要有选择的优化使用.jvm采取的措施是
- 3个关键字
    * volatile
    * synchronized
    * final
- 六项Happens-Before规则 (<font color=red>重点</font>)
   - 程序顺序性规则
   - volatile变量规则
   - 传递性
   - 管程中锁的规则
   - 线程中start规则
   - 线程join规则

## 1.三个关键字
### (1).volatile 
最原始的意思就是禁用cpu缓存,修饰词
```java
// 以下代码来源于【参考1】
class VolatileExample {
  int x = 0;
  volatile boolean v = false;
  public void writer() {
    x = 42;
    v = true;
  }
  public void reader() {
    if (v == true) {
      // 这里x会是多少呢？
    }
  }
}

```
这个例子x可能是0, 因为x可能因为cpu的缓存导致了可见性问题,所以现在的jdk是可以避免这个问题的原因是下面的Happens-Before规则导致
### (2).synchronized关键字
>以后会说,在Happens-Before规则也有说明
### (3).final关键字
volatile是告诉编译器不要使用cpu缓存和编译优化,但是final是告诉编译器这个变量生来不变,可以让编译器优化的更好一些.
## 2.Happens-Before规则
### (1).程序的顺序性规则
> 在一个线程中,前面的操作要可见于后面的操作,现在这一条规则可以完美解决上一个问题,对x的操作要对v可见,所以不会是0

### (2).volatile变量规则
>volatile变量的写操作要可见于对这个变量的读操作
### (3).传递性规则
>A可见于B,B可见于C,那么A可见于C

<font color=red>这里的规则一保证了同一个线程内的可见性,而第二个和第三个保证了在跨线程的时候能够保持可见性原因如下:</font>
>第一个线程写,第二个线程度,这两个就是有可见性,根据传递性,线程一的操作就对线程二的操作都具有了可见性

### (4).管程中的规则
>指对一个锁的解锁操作可见于对一个锁的加锁操作,如synchronized锁,操作完解锁,后来加锁进来的线程对之前的操作是可见的

### (5).线程的start()的规则
>主线程启动子线程,子线程能看到启动子线程之前的主线程的操作.

### (6).线程的join()的规则
>主线程等待子线程完成后,主线程能够看到子线程的操作.