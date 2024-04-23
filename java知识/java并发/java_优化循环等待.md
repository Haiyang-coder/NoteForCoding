[TOC]
# 优化循环等待----"等待--通知机制"
在破坏占用且等待条件的时候，如果转出账本和转入账本不满足同时在文件架上这个条件，就用死循环的方式来循环等待，核心代码如下
```java
// 一次性申请转出账户和转入账户，直到成功
while(!actr.apply(this, target)) ；
```
更好的方案应该是:如果线程要求的条件不满足，则线程阻塞自己，进入等待状态；当线程要求的条件满足后，通知等待的线程重新执行。其中，使用线程阻塞的方式就能**避免循环等待**消耗 CPU 的问题,即:
>线程首先获取互斥锁，当线程要求的条件不满足时，释放互斥锁，进入等待状态；当要求的条件满足时，通知等待的线程，重新获取互斥锁

## 1. 用synchronized 实现等待 – 通知机制
在 Java 语言里，等待 – 通知机制可以有多种实现方式，比如 Java 语言内置的 synchronized 配合 wait()、notify()、notifyAll() 这三个方法就能轻松实现
![](https://raw.githubusercontent.com/Haiyang-coder/ImageRepository/main/202201211508906.png)
我在上面这个图里为你大致描述了这个过程，当不满足条件的时候用wait让线程交出互斥锁,进入了等待队列.当条件满足时调用 notify()，会通知等待队列（互斥锁的等待队列）中的线程，告诉它条件<font color=red>曾经满足过</font>

为什么说是曾经满足过呢？因为 notify() 只能保证在通知时间点，条件是满足的。而被通知线程的执行时间点和通知的时间点基本上不会重合，所以当线程执行的时候，很可能条件已经不满足了（保不齐有其他线程插队）。这一点你需要格外注意

上面我们一直强调 wait()、notify()、notifyAll() 方法操作的等待队列是互斥锁的等待队列，所以如果 synchronized 锁定的是 this，那么对应的一定是 this.wait()、this.notify()、this.notifyAll()；如果 synchronized 锁定的是 target，那么对应的一定是 target.wait()、target.notify()、target.notifyAll() 。而且 wait()、notify()、notifyAll() 这三个方法能够被调用的前提是已经获取了相应的互斥锁，所以我们会发现 wait()、notify()、notifyAll() 都是在 synchronized{}内部被调用的。如果在 synchronized{}外部调用，或者锁定的 this，而用 target.wait() 调用的话，JVM 会抛出一个运行时异常：java.lang.IllegalMonitorStateExceptio

## 修改代码
```java
class Allocator {
  private List<Object> als;
  // 一次性申请所有资源
  synchronized void apply(
    Object from, Object to){
    // 经典写法
    while(als.contains(from) ||
         als.contains(to)){
      try{
        wait();
      }catch(Exception e){
      }   
    } 
    als.add(from);
    als.add(to);  
  }
  // 归还资源
  synchronized void free(
    Object from, Object to){
    als.remove(from);
    als.remove(to);
    notifyAll();
  }
}

```

在上面的代码中，我用的是 notifyAll() 来实现通知机制，为什么不使用 notify() 呢？这二者是有区别的，notify() 是会随机地通知等待队列中的一个线程，而 notifyAll() 会通知等待队列中的所有线程.
<font color=red>尽量使用notifyAll()</font>,这个办法会把所有的等待队列里面的线程唤醒,如果不这么用,只随机唤起一个,唤起的那一个刚好直接又进入的wait,那么就会永远等待下去.