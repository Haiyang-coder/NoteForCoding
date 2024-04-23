# muduo_base

学习大佬的设计思想，这比自己自己瞎弄能少走不少的弯路

## 时间类：Timestamp

简单明了的时间类

```c++
class Timestamp : public muduo::copyable,//可以拷贝的
                  public boost::equality_comparable<Timestamp>,
                  public boost::less_than_comparable<Timestamp>//你只要实现了小于号和等号运算符，他给你自动推断实现大于，大于等于，小于等于····
{
public:
  ///
  /// Constucts an invalid Timestamp.
  ///
  Timestamp()
    : microSecondsSinceEpoch_(0)
  {
  }

  ///
  /// Constucts a Timestamp at specific time
  ///
  /// @param microSecondsSinceEpoch
  explicit Timestamp(int64_t microSecondsSinceEpochArg)
    : microSecondsSinceEpoch_(microSecondsSinceEpochArg)
  {
  }

  void swap(Timestamp& that)
  {
    std::swap(microSecondsSinceEpoch_, that.microSecondsSinceEpoch_);
  }

  // default copy/assignment/dtor are Okay

  string toString() const;
  string toFormattedString(bool showMicroseconds = true) const;

  bool valid() const { return microSecondsSinceEpoch_ > 0; }

  // for internal usage.
  int64_t microSecondsSinceEpoch() const { return microSecondsSinceEpoch_; }
  time_t secondsSinceEpoch() const
  { return static_cast<time_t>(microSecondsSinceEpoch_ / kMicroSecondsPerSecond); }

  ///
  /// Get time of now.
  ///
  static Timestamp now();
  static Timestamp invalid()
  {
    return Timestamp();
  }

  static Timestamp fromUnixTime(time_t t)
  {
    return fromUnixTime(t, 0);
  }

  static Timestamp fromUnixTime(time_t t, int microseconds)
  {
    return Timestamp(static_cast<int64_t>(t) * kMicroSecondsPerSecond + microseconds);
  }

  static const int kMicroSecondsPerSecond = 1000 * 1000;

 private:
  //只有这个数据成员用来表示时间
  //距离1971-1-1 的微秒数
  int64_t microSecondsSinceEpoch_; 
};

inline bool operator<(Timestamp lhs, Timestamp rhs)
{
  return lhs.microSecondsSinceEpoch() < rhs.microSecondsSinceEpoch();
}

inline bool operator==(Timestamp lhs, Timestamp rhs)
{
  return lhs.microSecondsSinceEpoch() == rhs.microSecondsSinceEpoch();
}

///
/// Gets time difference of two timestamps, result in seconds.
///
/// @param high, low
/// @return (high-low) in seconds
/// @c double has 52-bit precision, enough for one-microsecond
/// resolution for next 100 years.
inline double timeDifference(Timestamp high, Timestamp low)
{
  int64_t diff = high.microSecondsSinceEpoch() - low.microSecondsSinceEpoch();
  return static_cast<double>(diff) / Timestamp::kMicroSecondsPerSecond;//这是一个define 1000* 1000相当于返回的是秒数，两个数字相差的秒数
}

///
/// Add @c seconds to given timestamp.
///
/// @return timestamp+seconds as Timestamp
///
inline Timestamp addTime(Timestamp timestamp, double seconds)
{
  int64_t delta = static_cast<int64_t>(seconds * Timestamp::kMicroSecondsPerSecond);
  return Timestamp(timestamp.microSecondsSinceEpoch() + delta);
}

}
```





## 原子操作的类：AtomicIntegerT

这个类主要是解决多线程中对一个对象的简单的加减法操作，包括自增自减

**头文件**

``` c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_ATOMIC_H
#define MUDUO_BASE_ATOMIC_H

#include "muduo/base/noncopyable.h"

#include <stdint.h>

namespace muduo
{

namespace detail
{
template<typename T>
class AtomicIntegerT : noncopyable
{
 public:
  AtomicIntegerT()
    : value_(0)
  {
  }

  // uncomment if you need copying and assignment
  //
  // AtomicIntegerT(const AtomicIntegerT& that)
  //   : value_(that.get())
  // {}
  //
  // AtomicIntegerT& operator=(const AtomicIntegerT& that)
  // {
  //   getAndSet(that.get());
  //   return *this;
  // }

  T get()
  {
    // in gcc >= 4.7: __atomic_load_n(&value_, __ATOMIC_SEQ_CST)
    return __sync_val_compare_and_swap(&value_, 0, 0);
      //比较一下当前value的值是否等于0
      //等于：value == 0 返回0
      //如果不等：不修改，返回value之前的值
  }

  T getAndAdd(T x)
  {
    // in gcc >= 4.7: __atomic_fetch_add(&value_, x, __ATOMIC_SEQ_CST)
    return __sync_fetch_and_add(&value_, x);
  }

  T addAndGet(T x)
  {
    return getAndAdd(x) + x;
  }

  T incrementAndGet()
  {
    return addAndGet(1);
  }

  T decrementAndGet()
  {
    return addAndGet(-1);
  }

  void add(T x)
  {
    getAndAdd(x);
  }

  void increment()
  {
    incrementAndGet();
  }

  void decrement()
  {
    decrementAndGet();
  }

  T getAndSet(T newValue)
  {
    // in gcc >= 4.7: __atomic_exchange_n(&value_, newValue, __ATOMIC_SEQ_CST)
    return __sync_lock_test_and_set(&value_, newValue);
  }

 private:
  volatile T value_;//防止编译器对这个代码进行优化
    
};
}  // namespace detail

typedef detail::AtomicIntegerT<int32_t> AtomicInt32;
typedef detail::AtomicIntegerT<int64_t> AtomicInt64;

}  // namespace muduo

#endif  // MUDUO_BASE_ATOMIC_H

```



1. **type _sync_val_compare_and_swap(type *ptr, type expected, type new_value);**

> `_sync_val_compare_and_swap` 是一个与原子操作相关的函数，通常用于多线程或并发编程中。该函数的作用是比较内存中的值与预期值，如果相等，则将新值写入内存，并返回之前的值。这个操作是原子的，意味着在执行期间不会被中断，从而保证了线程安全性。
>
> - `ptr` 是指向要修改的内存位置的指针。
> - `expected` 是预期的值，即当前内存中的值应该与之相等。
> - `new_value` 是要写入内存的新值。
>
> 函数执行后，会比较 `*ptr` 与 `expected` 是否相等，如果相等，则将 `new_value` 写入 `*ptr`，并返回之前的值；如果不相等，则不进行修改，直接返回当前的值。
>
> 这种操作在并发编程中常用于实现各种同步原语，例如锁、信号量等，以确保多线程程序的正确性。

2. **type __sync_fetch_and_add(type *ptr, type value);**

> 是一个原子操作函数，通常用于多线程或并发编程中。它的作用是将指定内存位置的值与一个给定的增量相加，并返回相加前的值。这个操作是原子的，即在执行期间不会被中断，从而确保线程安全性。
>
> - `ptr` 是指向要修改的内存位置的指针。
> - `value` 是要与内存中的当前值相加的增量。
>
> 函数执行后，会将 `*ptr` 的当前值返回(==返回的是没有修改过的值==)，并将 `*ptr` 的值增加 `value`。由于这两个操作是原子的，所以可以确保在多线程环境中对共享变量的安全增加。

3.  **type __sync_lock_test_and_set(type *ptr, type value);**

> 是一个原子操作函数，通常用于多线程或并发编程中。它的作用是将指定内存位置的值与一个给定的增量相加，并返回相加前的值。这个操作是原子的，即在执行期间不会被中断，从而确保线程安全性。
>
> - `ptr` 是指向要修改的内存位置的指针。
> - `value` 是要设置的新值。
>
> 函数执行后，会将 `*ptr` 的当前值返回(==返回的是没有修改过的值==)，并将 `*ptr` 的值设置为 `value`。由于这两个操作是原子的，所以可以确保在多线程环境中对共享变量的安全设置。

4. **type _sync_bool_compare_and_swap(type *ptr, type expected, type new_value);**

> `_sync_val_compare_and_swap` 是一个与原子操作相关的函数，通常用于多线程或并发编程中。该函数的作用是比较内存中的值与预期值，如果相等，则将新值写入内存，并返回之前的值。这个操作是原子的，意味着在执行期间不会被中断，从而保证了线程安全性。
>
> - `ptr` 是指向要修改的内存位置的指针。
> - `expected` 是预期的值，即当前内存中的值应该与之相等。
> - `new_value` 是要写入内存的新值。
>
> 函数执行后，会比较 `*ptr` 与 `expected` 是否相等，如果相等，则将 `new_value` 写入 `*ptr`，并返回true。如果不相等，则不进行修改，直接返回false
>
> 这种操作在并发编程中常用于实现各种同步原语，例如锁、信号量等，以确保多线程程序的正确性。





**无锁队列的实现**：https://coolshell.cn/articles/8239.html



**volatile关键字：**

> 1. **禁止编译器优化：** `volatile` 告诉编译器不要对声明为 `volatile` 的变量进行任何优化，因为这些变量的值可能会在程序执行期间被外部因素更改，而编译器无法感知这些变化。
> 2. **防止缓存优化：** 编译器在优化代码时可能会使用寄存器或内部缓存来存储变量的值，而不是直接访问内存。使用 `volatile` 可以确保每次访问该变量时都会从内存中读取最新的值，而不是使用缓存中的旧值。
> 3. **适用于多线程环境：** 在多线程环境中，一个线程对变量的修改可能不会立即被其他线程看到，除非该变量被声明为 `volatile`。这是因为编译器或硬件可能对变量的读写进行重排序或缓存，而 `volatile` 可以帮助确保变量的可见性。
> 4. **硬件访问：** 在嵌入式系统或与硬件直接交互的情况下，`volatile` 通常用于声明与硬件相关的寄存器，以确保编译器不会对这些寄存器的访问进行优化。

**总结：**

这个类的设计依赖上面的函数，目的是实现加减的原子操作，好处就是不用锁来完成简单的加减匀算，还记得吗。频繁的锁的切换等待是服务器性能的四大杀手之一。但是这个类的使用依赖你的cpu可以支持这些指令，编译的时候也要有一个编译选项。你就直接用muduo给你封装好的就行，不用这么麻烦了

## 异常类：Exception

**头文件：**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_EXCEPTION_H
#define MUDUO_BASE_EXCEPTION_H

#include "muduo/base/Types.h"
#include <exception>

namespace muduo
{

class Exception : public std::exception//继承自标准模板库的exception类
{
 public:
  Exception(string what);
  ~Exception() noexcept override = default;

  // default copy-ctor and operator= are okay.

  const char* what() const noexcept override
  {
    return message_.c_str();
  }

  const char* stackTrace() const noexcept
  {
    return stack_.c_str();
  }

 private:
  string message_;//异常信息的字符串
  string stack_;//保存异常发生的时候调用函数的栈回收信息
};

}  // namespace muduo

#endif 
```

**cpp文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/base/Exception.h"
#include "muduo/base/CurrentThread.h"

namespace muduo
{

  Exception::Exception(string msg)
      : message_(std::move(msg)),
        stack_(CurrentThread::stackTrace(/*demangle=*/false))//这个类唯一一个重要的方法被在其他区域实现了
            //我给你复制到下面
  {
  }

} // namespace muduo


//下面的代码是从其他地方拷贝过来的，不属于muduo的Exception类
//下面的这个CurrentThread类原本是在thread.cc文件里面，而且也没有stackTrace这个方法


namespace muduo
{
namespace CurrentThread
{
__thread int t_cachedTid = 0;
__thread char t_tidString[32];
__thread int t_tidStringLength = 6;
__thread const char* t_threadName = "unknown";
static_assert(std::is_same<int, pid_t>::value, "pid_t should be int");

string stackTrace(bool demangle)
{
  string stack;
  const int max_frames = 200;
  void* frame[max_frames];
  int nptrs = ::backtrace(frame, max_frames);//这个函数很重要，下面会详细解释一下他
  char** strings = ::backtrace_symbols(frame, nptrs);//这个函数也是重要
  if (strings)
  {
    size_t len = 256;
    char* demangled = demangle ? static_cast<char*>(::malloc(len)) : nullptr;
    for (int i = 1; i < nptrs; ++i)  // skipping the 0-th, which is this function
    {
      if (demangle)
      {
        // https://panthema.net/2008/0901-stacktrace-demangled/
        // bin/exception_test(_ZN3Bar4testEv+0x79) [0x401909]
        char* left_par = nullptr;
        char* plus = nullptr;
        for (char* p = strings[i]; *p; ++p)
        {
          if (*p == '(')
            left_par = p;
          else if (*p == '+')
            plus = p;
        }

        if (left_par && plus)
        {
          *plus = '\0';
          int status = 0;
          char* ret = abi::__cxa_demangle(left_par+1, demangled, &len, &status);
          *plus = '+';
          if (status == 0)
          {
            demangled = ret;  // ret could be realloc()
            stack.append(strings[i], left_par+1);
            stack.append(demangled);
            stack.append(plus);
            stack.push_back('\n');
            continue;
          }
        }
      }
      // Fallback to mangled names
      stack.append(strings[i]);
      stack.push_back('\n');
    }
    free(demangled);
    free(strings);
  }
  return stack;
}

}  // namespace CurrentThread
}  // namespace muduo


```

 **int backtrace(void\** buffer, int size);**

栈回溯，保存各个栈帧的地址

> `backtrace` 函数是一个用于获取当前线程调用栈信息的函数。它通常用于调试和错误诊断，可以在程序运行时获取函数调用栈的信息，包括函数的调用顺序、调用关系以及对应的函数名和地址等。
>
> - `buffer` 是一个指向 `void*` 类型指针的数组，用于存储获取到的调用栈信息。
> - `size` 是数组的大小，表示可以存储多少个调用栈帧的信息。

**char\** backtrace_symbols(void* const* buffer, int size);**

根据栈地址，转成相应的函数符号

> `backtrace_symbols` 函数是与 `backtrace` 函数一起使用的工具函数，用于将 `backtrace` 获取到的函数地址转换为可读的函数名和源文件信息。它通常用于调试和错误诊断，以便更好地理解程序在执行时经过的函数调用路径。
>
> - `buffer` 是由 `backtrace` 函数填充的函数地址数组。
> - `size` 是数组的大小，即调用栈帧的数量。
>
> `backtrace_symbols` 函数会返回一个指向字符串数组的指针，每个字符串表示一个函数调用栈帧的信息，包括函数名和源文件信息。
>
> 使用 `backtrace` 和 `backtrace_symbols` 的一般步骤如下：
>
> 1. 调用 `backtrace` 函数获取函数地址数组。
> 2. 将获取到的函数地址数组传递给 `backtrace_symbols` 函数。
> 3. `backtrace_symbols` 函数会返回一个字符串数组，每个字符串表示一个调用栈帧的信息。
> 4. 遍历字符串数组，可以获取每个调用栈帧的详细信息，包括函数名和源文件信息。
> 5. 使用获取到的信息进行调试或错误诊断。



## 线程封装类：Thread

在linux中，每一个进程都有一个pid，类型是`pid_t`是由`getpid()`取得的。linux下的POSIX线程也有一个id，类型是`pthread_t`，是由`pthread_self`取得的，这个`pthread_t`是由线程库维护的，他的id的空间每个进程都是相互独立的（即不同的进程中的两个线程可以有相同的`pthread_t`）.linux的POSIX线程库实现的线程其实也是一个进程，只是该进程与主进程（启动线程的的进程）共享一些资源而已，比如代码段，数据段。

有时候我们可能需要直到进程的真实`pid`。比如进程P1要向另一个进程P2中的某个线程发送一个信号，我们既不能使用进程P2的pid，更不能使用线程的`pthread_id`，而只能使用该线程的真实pid，称为tid

有一个函数`gettid()`可以取得tid，但是glibc没有实现这个函数，只能通过linux的系统调用`syscall`来获取`syacall(SYS_gettid)`

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_THREAD_H
#define MUDUO_BASE_THREAD_H

#include "muduo/base/Atomic.h"
#include "muduo/base/CountDownLatch.h"
#include "muduo/base/Types.h"

#include <functional>
#include <memory>
#include <pthread.h>

namespace muduo
{

class Thread : noncopyable
{
 public:
  typedef std::function<void ()> ThreadFunc;

  explicit Thread(ThreadFunc, const string& name = string());
  // FIXME: make it movable in C++11
  ~Thread();

  void start();
  int join(); // return pthread_join()

  bool started() const { return started_; }
  // pthread_t pthreadId() const { return pthreadId_; }
  pid_t tid() const { return tid_; }
  const string& name() const { return name_; }

  static int numCreated() { return numCreated_.get(); }

 private:
  void setDefaultName();

  bool       started_;
  bool       joined_;
  pthread_t  pthreadId_;
  pid_t      tid_;
  ThreadFunc func_;
  string     name_;
  CountDownLatch latch_;

  static AtomicInt32 numCreated_;
};

}  // namespace muduo
#endif  // MUDUO_BASE_THREAD_H

```

**Thread.cc**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/base/Thread.h"
#include "muduo/base/CurrentThread.h"
#include "muduo/base/Exception.h"
#include "muduo/base/Logging.h"

#include <type_traits>

#include <errno.h>
#include <stdio.h>
#include <unistd.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <sys/types.h>
#include <linux/unistd.h>

namespace muduo
{
namespace CurrentThread
{
//__thread:保证了每个线程都是独一份的变量，而不是
__thread: int t_cachedTid = 0;//把线程真实的tid给缓存起来，减少系统调用的次数
__thread char t_tidString[32];//tid的字符串表示形式 
__thread int t_tidStringLength = 6;
__thread const char* t_threadName = "unknown";
static_assert(std::is_same<int, pid_t>::value, "pid_t should be int");
}
    
    
namespace detail
{

pid_t gettid()
{
  return static_cast<pid_t>(::syscall(SYS_gettid));
}

void afterFork()
{
  muduo::CurrentThread::t_cachedTid = 0;
  muduo::CurrentThread::t_threadName = "main";
  CurrentThread::tid();
  // no need to call pthread_atfork(NULL, NULL, &afterFork);
}

class ThreadNameInitializer
{
 public:
  ThreadNameInitializer()
  {
    muduo::CurrentThread::t_threadName = "main";
    CurrentThread::tid();
    pthread_atfork(NULL, NULL, &afterFork);
      //不要编写多进程多线程的程序，很容易就嗝屁了
  }
};

ThreadNameInitializer init;

struct ThreadData
{
  typedef muduo::Thread::ThreadFunc ThreadFunc;
  ThreadFunc func_;
  string name_;
  pid_t* tid_;
  CountDownLatch* latch_;

  ThreadData(ThreadFunc func,
             const string& name,
             pid_t* tid,
             CountDownLatch* latch)
    : func_(std::move(func)),
      name_(name),
      tid_(tid),
      latch_(latch)
  { }

  void runInThread()
  {
    *tid_ = muduo::CurrentThread::tid();
    tid_ = NULL;
    latch_->countDown();
    latch_ = NULL;

    muduo::CurrentThread::t_threadName = name_.empty() ? "muduoThread" : name_.c_str();
    ::prctl(PR_SET_NAME, muduo::CurrentThread::t_threadName);
    try
    {
      func_();
      muduo::CurrentThread::t_threadName = "finished";
    }
    catch (const Exception& ex)
    {
      muduo::CurrentThread::t_threadName = "crashed";
      fprintf(stderr, "exception caught in Thread %s\n", name_.c_str());
      fprintf(stderr, "reason: %s\n", ex.what());
      fprintf(stderr, "stack trace: %s\n", ex.stackTrace());
      abort();
    }
    catch (const std::exception& ex)
    {
      muduo::CurrentThread::t_threadName = "crashed";
      fprintf(stderr, "exception caught in Thread %s\n", name_.c_str());
      fprintf(stderr, "reason: %s\n", ex.what());
      abort();
    }
    catch (...)
    {
      muduo::CurrentThread::t_threadName = "crashed";
      fprintf(stderr, "unknown exception caught in Thread %s\n", name_.c_str());
      throw; // rethrow
    }
  }
};

void* startThread(void* obj)
{
  ThreadData* data = static_cast<ThreadData*>(obj);
  data->runInThread();
  delete data;
  return NULL;
}

}  // namespace detail

void CurrentThread::cacheTid()
{
  if (t_cachedTid == 0)
  {
    t_cachedTid = detail::gettid();
    t_tidStringLength = snprintf(t_tidString, sizeof t_tidString, "%5d ", t_cachedTid);
  }
}

bool CurrentThread::isMainThread()
{
  return tid() == ::getpid();
}

void CurrentThread::sleepUsec(int64_t usec)
{
  struct timespec ts = { 0, 0 };
  ts.tv_sec = static_cast<time_t>(usec / Timestamp::kMicroSecondsPerSecond);
  ts.tv_nsec = static_cast<long>(usec % Timestamp::kMicroSecondsPerSecond * 1000);
  ::nanosleep(&ts, NULL);
}

AtomicInt32 Thread::numCreated_;

Thread::Thread(ThreadFunc func, const string& n)
  : started_(false),
    joined_(false),
    pthreadId_(0),
    tid_(0),
    func_(std::move(func)),
    name_(n),
    latch_(1)
{
  setDefaultName();
}

Thread::~Thread()
{
  if (started_ && !joined_)
  {
    pthread_detach(pthreadId_);
  }
}

void Thread::setDefaultName()
{
  int num = numCreated_.incrementAndGet();
  if (name_.empty())
  {
    char buf[32];
    snprintf(buf, sizeof buf, "Thread%d", num);
    name_ = buf;
  }
}

void Thread::start()
{
  assert(!started_);
  started_ = true;
  // FIXME: move(func_)
  detail::ThreadData* data = new detail::ThreadData(func_, name_, &tid_, &latch_);
  if (pthread_create(&pthreadId_, NULL, &detail::startThread, data))
  {
    started_ = false;
    delete data; // or no delete?
    LOG_SYSFATAL << "Failed in pthread_create";
  }
  else
  {
    latch_.wait();
    assert(tid_ > 0);
  }
}

int Thread::join()
{
  assert(started_);
  assert(!joined_);
  joined_ = true;
  return pthread_join(pthreadId_, NULL);
}

}  // namespace muduo

```



**__thread**

> `__thread` 是一个用于声明线程局部存储（Thread-Local Storage，TLS）变量的关键字。它告诉编译器，该变量对每个线程都是独立的，每个线程都拥有自己的变量实例，互不影响。`__thread` 关键字通常用于多线程编程环境，以提供线程间独立的存储空间。
>
> 在使用 `__thread` 关键字声明变量时，每个线程都会有自己的该变量的副本，而不同线程之间的修改不会相互影响。这对于需要在线程之间保持状态或避免共享变量带来的竞态条件非常有用。
>
> 1. **线程安全：** 变量在每个线程中都有独立的实例，因此不存在线程间的竞态条件。
> 2. **避免锁的开销：** 对于只在单个线程中使用的变量，不必使用锁进行同步，从而避免了锁的开销。
> 3. **提高性能：** 由于每个线程都有自己的变量实例，因此避免了共享变量引起的缓存同步等开销，有助于提高性能。

这个关键字只能修饰POD类型，与c兼容的原始数据类型，例如结构和整形等c语言中的类型是pod类型，但带有用户定义的构造函数或者虚函数类则不是（==不能调用构造函数==）

****

**int pthread_atfork(void (*prepare)(void), void (*parent)(void), void (*child)(void));**

> `pthread_atfork` 函数是用于注册在`fork`系统调用期间调用的处理函数的 POSIX 线程库函数。`fork`系统调用用于创建一个新 进程，该进程是调用进程的副本。由于 `fork` 会在父进程和子进程之间复制整个地址空间，包括线程的状态，因此在多线程程序中使用 `fork` 可能会导致一些问题。
>
> - `prepare` 函数在调用 `fork` 之前会在父进程中执行，用于在 `fork` 开始之前锁住全局资源，以防止竞态条件。
> - `parent` 函数在父进程中的 `fork` 返回之后、子进程开始执行之前执行，用于在父进程中释放锁、解锁资源等。
> - `child` 函数在子进程中的 `fork` 返回之后执行，用于在子进程中释放锁、解锁资源等。
>
> 通过使用 `pthread_atfork` 注册的处理函数，可以确保在 `fork` 过程中的关键时刻执行特定的操作，从而避免父子进程之间的竞态条件或资源冲突。

## 互斥锁： mutex

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_MUTEX_H
#define MUDUO_BASE_MUTEX_H

#include "muduo/base/CurrentThread.h"
#include "muduo/base/noncopyable.h"
#include <assert.h>
#include <pthread.h>

// Thread safety annotations {
// https://clang.llvm.org/docs/ThreadSafetyAnalysis.html

// Enable thread safety attributes only with clang.
// The attributes can be safely erased when compiling with other compilers.
#if defined(__clang__) && (!defined(SWIG))
#define THREAD_ANNOTATION_ATTRIBUTE__(x)   __attribute__((x))
#else
#define THREAD_ANNOTATION_ATTRIBUTE__(x)   // no-op
#endif

#define CAPABILITY(x) \
  THREAD_ANNOTATION_ATTRIBUTE__(capability(x))

#define SCOPED_CAPABILITY \
  THREAD_ANNOTATION_ATTRIBUTE__(scoped_lockable)

#define GUARDED_BY(x) \
  THREAD_ANNOTATION_ATTRIBUTE__(guarded_by(x))

#define PT_GUARDED_BY(x) \
  THREAD_ANNOTATION_ATTRIBUTE__(pt_guarded_by(x))

#define ACQUIRED_BEFORE(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(acquired_before(__VA_ARGS__))

#define ACQUIRED_AFTER(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(acquired_after(__VA_ARGS__))

#define REQUIRES(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(requires_capability(__VA_ARGS__))

#define REQUIRES_SHARED(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(requires_shared_capability(__VA_ARGS__))

#define ACQUIRE(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(acquire_capability(__VA_ARGS__))

#define ACQUIRE_SHARED(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(acquire_shared_capability(__VA_ARGS__))

#define RELEASE(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(release_capability(__VA_ARGS__))

#define RELEASE_SHARED(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(release_shared_capability(__VA_ARGS__))

#define TRY_ACQUIRE(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(try_acquire_capability(__VA_ARGS__))

#define TRY_ACQUIRE_SHARED(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(try_acquire_shared_capability(__VA_ARGS__))

#define EXCLUDES(...) \
  THREAD_ANNOTATION_ATTRIBUTE__(locks_excluded(__VA_ARGS__))

#define ASSERT_CAPABILITY(x) \
  THREAD_ANNOTATION_ATTRIBUTE__(assert_capability(x))

#define ASSERT_SHARED_CAPABILITY(x) \
  THREAD_ANNOTATION_ATTRIBUTE__(assert_shared_capability(x))

#define RETURN_CAPABILITY(x) \
  THREAD_ANNOTATION_ATTRIBUTE__(lock_returned(x))

#define NO_THREAD_SAFETY_ANALYSIS \
  THREAD_ANNOTATION_ATTRIBUTE__(no_thread_safety_analysis)

// End of thread safety annotations }

#ifdef CHECK_PTHREAD_RETURN_VALUE

#ifdef NDEBUG
__BEGIN_DECLS
extern void __assert_perror_fail (int errnum,
                                  const char *file,
                                  unsigned int line,
                                  const char *function)
    noexcept __attribute__ ((__noreturn__));
__END_DECLS
#endif

#define MCHECK(ret) ({ __typeof__ (ret) errnum = (ret);         \
                       if (__builtin_expect(errnum != 0, 0))    \
                         __assert_perror_fail (errnum, __FILE__, __LINE__, __func__);})

#else  // CHECK_PTHREAD_RETURN_VALUE

#define MCHECK(ret) ({ __typeof__ (ret) errnum = (ret);         \
                       assert(errnum == 0); (void) errnum;})

#endif // CHECK_PTHREAD_RETURN_VALUE

namespace muduo
{

// Use as data member of a class, eg.
//
// class Foo
// {
//  public:
//   int size() const;
//
//  private:
//   mutable MutexLock mutex_;
//   std::vector<int> data_ GUARDED_BY(mutex_);
// };
class CAPABILITY("mutex") MutexLock : noncopyable
{
 public:
  MutexLock()
    : holder_(0)//表示这个锁没有被任何线程拥有
  {
        //构造函数中初始化这个锁
    MCHECK(pthread_mutex_init(&mutex_, NULL));
  }

  ~MutexLock()
  {
    assert(holder_ == 0);//表示这个锁没有被任何线程拥有
    MCHECK(pthread_mutex_destroy(&mutex_));//销毁锁
  }

  // must be called when locked, i.e. for assertion
  bool isLockedByThisThread() const
  {
    return holder_ == CurrentThread::tid();
  }

  void assertLocked() const ASSERT_CAPABILITY(this)
  {
    assert(isLockedByThisThread());
  }

  // internal usage

  void lock() ACQUIRE()
  {
    MCHECK(pthread_mutex_lock(&mutex_));//加锁
    assignHolder();//注册锁的拥有者
  }

  void unlock() RELEASE()
  {
    unassignHolder();//解除锁的拥有者
    MCHECK(pthread_mutex_unlock(&mutex_));//解锁
  }

  pthread_mutex_t* getPthreadMutex() /* non-const */
  {
    return &mutex_;
  }

 private:
  friend class Condition;

  class UnassignGuard : noncopyable
  {
   public:
    explicit UnassignGuard(MutexLock& owner)
      : owner_(owner)
    {
      owner_.unassignHolder();
    }

    ~UnassignGuard()
    {
      owner_.assignHolder();
    }

   private:
    MutexLock& owner_;
  };

  void unassignHolder()
  {
    holder_ = 0;
  }

  void assignHolder()
  {
    holder_ = CurrentThread::tid();
  }

    //类的两个成员变量
  pthread_mutex_t mutex_;
    //用线程的tid来表示拥有该锁的线程
  pid_t holder_;
};

// Use as a stack variable, eg.
// int Foo::size() const
// {
//   MutexLockGuard lock(mutex_);
//   return data_.size();
// }
class SCOPED_CAPABILITY MutexLockGuard : noncopyable
{//RAII方式封装，简简单单的使用mutex
    //必须是基于MutexLock，不能单独使用
 public:
  explicit MutexLockGuard(MutexLock& mutex) ACQUIRE(mutex)
    : mutex_(mutex)
  {
        //构造函数的时候获取资源
    mutex_.lock();
  }

  ~MutexLockGuard() RELEASE()
  {
      //析构的时候释放资源
    mutex_.unlock();
  }

 private:

  MutexLock& mutex_;
};

}  // namespace muduo

// Prevent misuse like:
// MutexLockGuard(mutex_);
// A tempory object doesn't hold the lock for long!
#define MutexLockGuard(x) error "Missing guard object name"

#endif  // MUDUO_BASE_MUTEX_H

```

头文件有两个类，`MutexLock` 还有`MutexLockGuard`

## 条件变量： Condition

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_CONDITION_H
#define MUDUO_BASE_CONDITION_H

#include "muduo/base/Mutex.h"

#include <pthread.h>

namespace muduo
{

class Condition : noncopyable
{
 public:
  explicit Condition(MutexLock& mutex)
    : mutex_(mutex)
  {
    MCHECK(pthread_cond_init(&pcond_, NULL));//
  }

  ~Condition()
  {
    MCHECK(pthread_cond_destroy(&pcond_));
  }

  void wait()
  {
    MutexLock::UnassignGuard ug(mutex_);//先加锁
    MCHECK(pthread_cond_wait(&pcond_, mutex_.getPthreadMutex()));//然后等待
  }

  // returns true if time out, false otherwise.
  bool waitForSeconds(double seconds);

  void notify()
  {
    MCHECK(pthread_cond_signal(&pcond_));//唤醒其中一个等待的资源
  }

  void notifyAll()
  {
    MCHECK(pthread_cond_broadcast(&pcond_));//唤醒所有等待的资源，让他们取竞争
  }

 private:
  MutexLock& mutex_;
  pthread_cond_t pcond_;
};

}  // namespace muduo

#endif  // MUDUO_BASE_CONDITION_H

```

**cpp文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/base/Condition.h"

#include <errno.h>

// returns true if time out, false otherwise.
bool muduo::Condition::waitForSeconds(double seconds)
{
  struct timespec abstime;
  // FIXME: use CLOCK_MONOTONIC or CLOCK_MONOTONIC_RAW to prevent time rewind.
  clock_gettime(CLOCK_REALTIME, &abstime);

  const int64_t kNanoSecondsPerSecond = 1000000000;
  int64_t nanoseconds = static_cast<int64_t>(seconds * kNanoSecondsPerSecond);

  abstime.tv_sec += static_cast<time_t>((abstime.tv_nsec + nanoseconds) / kNanoSecondsPerSecond);
  abstime.tv_nsec = static_cast<long>((abstime.tv_nsec + nanoseconds) % kNanoSecondsPerSecond);

  MutexLock::UnassignGuard ug(mutex_);
  return ETIMEDOUT == pthread_cond_timedwait(&pcond_, mutex_.getPthreadMutex(), &abstime);
}


```

条件变量的使用：
条件变量的使用我有详细的讲过，可以看我的笔记

## 倒计时门闩类： CountDownLatch

- 用于所有子线程等待主线程发起起跑
- 用于主线程等待子线程初始化完毕才开始工作

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_COUNTDOWNLATCH_H
#define MUDUO_BASE_COUNTDOWNLATCH_H

#include "muduo/base/Condition.h"
#include "muduo/base/Mutex.h"

namespace muduo
{

class CountDownLatch : noncopyable
{
 public:

  explicit CountDownLatch(int count);

  void wait();

  void countDown();

  int getCount() const;

 private:
  mutable MutexLock mutex_;
  Condition condition_ GUARDED_BY(mutex_);
  int count_ GUARDED_BY(mutex_);//计数器
};

}  // namespace muduo
#endif  // MUDUO_BASE_COUNTDOWNLATCH_H

```

**cpp文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/base/CountDownLatch.h"

using namespace muduo;

CountDownLatch::CountDownLatch(int count)
  : mutex_(),
    condition_(mutex_),
    count_(count)//这个就是这个类要等待的资源变量
{
}

void CountDownLatch::wait()
{
  MutexLockGuard lock(mutex_);
  while (count_ > 0)
  {
    condition_.wait();
  }
}

void CountDownLatch::countDown()
{
  MutexLockGuard lock(mutex_);
  --count_;
  if (count_ == 0)
  {
    condition_.notifyAll();
  }
}

int CountDownLatch::getCount() const
{
  MutexLockGuard lock(mutex_);
  return count_;
}


```

**mutable关键字**

> const 修饰的方法，不能改变成员变量的状态，但是mutable修饰的成员是个例外

## 两个缓冲区队列的实现

### 1. 无界缓冲区：BlockinngQueue\<T>

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_BLOCKINGQUEUE_H
#define MUDUO_BASE_BLOCKINGQUEUE_H

#include "muduo/base/Condition.h"
#include "muduo/base/Mutex.h"

#include <deque>
#include <assert.h>

namespace muduo
{

template<typename T>
class BlockingQueue : noncopyable
{
 public:
  using queue_type = std::deque<T>;

  BlockingQueue()
    : mutex_(),
      notEmpty_(mutex_),
      queue_()
  {
  }

  void put(const T& x)
  {
    MutexLockGuard lock(mutex_);
    queue_.push_back(x);
    notEmpty_.notify(); // wait morphing saves us
    // http://www.domaigne.com/blog/computing/condvars-signal-with-mutex-locked-or-not/
      //他这里把唤醒的操作也放入了锁的范围内了
  }

  void put(T&& x)
  {
    MutexLockGuard lock(mutex_);
    queue_.push_back(std::move(x));
    notEmpty_.notify();//我也应该做一个这种的方法，减少容器中任务的拷贝操作
  }

  T take()
  {
    MutexLockGuard lock(mutex_);
    // always use a while-loop, due to spurious wakeup
    while (queue_.empty())
    {
      notEmpty_.wait();
    }
    assert(!queue_.empty());
    T front(std::move(queue_.front()));
    queue_.pop_front();
    return front;
  }

  queue_type drain()
  {
    std::deque<T> queue;
    {
      MutexLockGuard lock(mutex_);
      queue = std::move(queue_);
      assert(queue_.empty());
    }
    return queue;
  }

  size_t size() const
  {
    MutexLockGuard lock(mutex_);
    return queue_.size();
  }

 private:
  mutable MutexLock mutex_;
  Condition         notEmpty_ GUARDED_BY(mutex_);
  queue_type        queue_ GUARDED_BY(mutex_);
};  // __attribute__ ((aligned (64)));

}  // namespace muduo

#endif  // MUDUO_BASE_BLOCKINGQUEUE_H

```

### 2. 有界缓冲区 BoundedBlockingQueue\<T>

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_BOUNDEDBLOCKINGQUEUE_H
#define MUDUO_BASE_BOUNDEDBLOCKINGQUEUE_H

#include "muduo/base/Condition.h"
#include "muduo/base/Mutex.h"

#include <boost/circular_buffer.hpp>
#include <assert.h>

namespace muduo
{

template<typename T>
class BoundedBlockingQueue : noncopyable
{
 public:
  explicit BoundedBlockingQueue(int maxSize)
    : mutex_(),
      notEmpty_(mutex_),
      notFull_(mutex_),
      queue_(maxSize)
  {
  }

  void put(const T& x)
  {
    MutexLockGuard lock(mutex_);
    while (queue_.full())
    {
      notFull_.wait();
    }
    assert(!queue_.full());
    queue_.push_back(x);
    notEmpty_.notify();
  }

  void put(T&& x)
  {
    MutexLockGuard lock(mutex_);
    while (queue_.full())
    {
      notFull_.wait();
    }
    assert(!queue_.full());
    queue_.push_back(std::move(x));
    notEmpty_.notify();
  }

  T take()
  {
    MutexLockGuard lock(mutex_);
    while (queue_.empty())
    {
      notEmpty_.wait();
    }
    assert(!queue_.empty());
    T front(std::move(queue_.front()));
    queue_.pop_front();
    notFull_.notify();
    return front;
  }

  bool empty() const
  {
    MutexLockGuard lock(mutex_);
    return queue_.empty();
  }

  bool full() const
  {
    MutexLockGuard lock(mutex_);
    return queue_.full();
  }

  size_t size() const
  {
    MutexLockGuard lock(mutex_);
    return queue_.size();
  }

  size_t capacity() const
  {
    MutexLockGuard lock(mutex_);
    return queue_.capacity();
  }

 private:
  mutable MutexLock          mutex_;
  Condition                  notEmpty_ GUARDED_BY(mutex_);
  Condition                  notFull_ GUARDED_BY(mutex_);
  boost::circular_buffer<T>  queue_ GUARDED_BY(mutex_);//用的boost库里面的环形缓冲区
};

}  // namespace muduo

#endif  // MUDUO_BASE_BOUNDEDBLOCKINGQUEUE_H

```

因为是有界的，所以用一个环形缓冲区，避免内存的反复申请

==我看好多地方都大量用了boost库的东西，所以抽时间一定学一下boost库==，看了一下这个类的代码 ，果然用了boost库封装好的东西，真的就是极大的方便了开发

## 线程池 ThreadPool

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_THREADPOOL_H
#define MUDUO_BASE_THREADPOOL_H

#include "muduo/base/Condition.h"
#include "muduo/base/Mutex.h"
#include "muduo/base/Thread.h"
#include "muduo/base/Types.h"

#include <deque>
#include <vector>

namespace muduo
{

class ThreadPool : noncopyable
{
 public:
  typedef std::function<void ()> Task;

  explicit ThreadPool(const string& nameArg = string("ThreadPool"));
  ~ThreadPool();

  // Must be called before start().
  void setMaxQueueSize(int maxSize) { maxQueueSize_ = maxSize; }
  void setThreadInitCallback(const Task& cb)
  { threadInitCallback_ = cb; }

  void start(int numThreads);
  void stop();

  const string& name() const
  { return name_; }

  size_t queueSize() const;

  // Could block if maxQueueSize > 0
  // Call after stop() will return immediately.
  // There is no move-only version of std::function in C++ as of C++14.
  // So we don't need to overload a const& and an && versions
  // as we do in (Bounded)BlockingQueue.
  // https://stackoverflow.com/a/25408989
  void run(Task f);

 private:
  bool isFull() const REQUIRES(mutex_);
  void runInThread();
  Task take();

  mutable MutexLock mutex_;
  Condition notEmpty_ GUARDED_BY(mutex_);
  Condition notFull_ GUARDED_BY(mutex_);
  string name_;
  Task threadInitCallback_;
  std::vector<std::unique_ptr<muduo::Thread>> threads_;//线程队列，使用了智能指针
  std::deque<Task> queue_ GUARDED_BY(mutex_);//任务队列，这里的队列是有容量限制的
  size_t maxQueueSize_;//最大的任务容量
  bool running_;//运行标志位
};

}  // namespace muduo

#endif  // MUDUO_BASE_THREADPOOL_H


```

**cpp文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/base/ThreadPool.h"

#include "muduo/base/Exception.h"

#include <assert.h>
#include <stdio.h>

using namespace muduo;

ThreadPool::ThreadPool(const string& nameArg)
  : mutex_(),
    notEmpty_(mutex_),
    notFull_(mutex_),
    name_(nameArg),
    maxQueueSize_(0),
    running_(false)
{
}

ThreadPool::~ThreadPool()
{
  if (running_)
  {
    stop();
  }
}

void ThreadPool::start(int numThreads)
{
  assert(threads_.empty());
  running_ = true;
  threads_.reserve(numThreads);
  for (int i = 0; i < numThreads; ++i)
  {
    char id[32];
    snprintf(id, sizeof id, "%d", i+1);
    threads_.emplace_back(new muduo::Thread(
          std::bind(&ThreadPool::runInThread, this), name_+id));
    threads_[i]->start();//开启了线程池中的工作线程也就是ThreadPool::runInThread
  }
  if (numThreads == 0 && threadInitCallback_)
  {
    threadInitCallback_();
  }
}

void ThreadPool::stop()
{
  {
  MutexLockGuard lock(mutex_);
  running_ = false;
  notEmpty_.notifyAll();
  notFull_.notifyAll();
  }
  for (auto& thr : threads_)
  {
    thr->join();
  }
}

size_t ThreadPool::queueSize() const
{
  MutexLockGuard lock(mutex_);
  return queue_.size();
}

void ThreadPool::run(Task task)
{
  if (threads_.empty())
  {
    task();//如果线程池是空的，也就是没有线程可以使用
  }
  else
  {
    MutexLockGuard lock(mutex_);
    while (isFull() && running_)
    {
      notFull_.wait();
    }
    if (!running_) return;
    assert(!isFull());

    queue_.push_back(std::move(task));//这里用了移动语义
    notEmpty_.notify();
  }
}

ThreadPool::Task ThreadPool::take()
{
  MutexLockGuard lock(mutex_);
  // always use a while-loop, due to spurious wakeup
  while (queue_.empty() && running_)
  {
    notEmpty_.wait();//任务队列为空的时候的时候就在这阻塞着
  }
  Task task;
  if (!queue_.empty())//这里看一下是否为空，因为还有一种可能是，还是空的，但是running是false
  {
      //不是空的，就取出任务
    task = queue_.front();
    queue_.pop_front();
    if (maxQueueSize_ > 0)
    {
      notFull_.notify();
    }
  }
  return task;
}

bool ThreadPool::isFull() const
{
  mutex_.assertLocked();
  return maxQueueSize_ > 0 && queue_.size() >= maxQueueSize_;
}

void ThreadPool::runInThread()
{
  try
  {
    if (threadInitCallback_)
    {
      threadInitCallback_();
    }
    while (running_)
    {
        //这个线程开启之后就会开始拿取任务
      Task task(take());
      if (task)
      {
        task();
      }
    }
  }
  catch (const Exception& ex)
  {
    fprintf(stderr, "exception caught in ThreadPool %s\n", name_.c_str());
    fprintf(stderr, "reason: %s\n", ex.what());
    fprintf(stderr, "stack trace: %s\n", ex.stackTrace());
    abort();
  }
  catch (const std::exception& ex)
  {
    fprintf(stderr, "exception caught in ThreadPool %s\n", name_.c_str());
    fprintf(stderr, "reason: %s\n", ex.what());
    abort();
  }
  catch (...)
  {
    fprintf(stderr, "unknown exception caught in ThreadPool %s\n", name_.c_str());
    throw; // rethrow
  }
}


```



**随笔**

1. 我也实现了一个线程池，我的缺点就是我的任务队列的函数所需要的数据我是用的`void*`来定义的，也就是说线程池的使用者想要往线程池中传递不一样的线程函数都需要，做一个封装的函数，来适配我的线程池。

   ```c++
   using  ThreadPollCallBack = void*(* )(void *arg);
   struct TaskNode
   {
      TaskNode()
       {
           function = nullptr;
           arg = nullptr;
       }
       TaskNode(ThreadPollCallBack func, void* arg)
       {
           function = func;
           this->arg = arg;
       }
       ThreadPollCallBack function;
       void* arg;
   };
   //这就是设计的任务节点，每个想要使用我的线程池必须使用这种函数形式void*(* )(void *arg);然后在这这个函数里面在调用一下自己的函数
   ```

   muduo用了`std::function<void ()>`作为了任务的节点，可以看出来给这个线程池传递的函数的类型是`void()`即没有参数也没有返回值的类型。我想在用这个线程池往线程池传递任务函数的时候，==想要用户用boost::bind==这个函数来绑定你想要传递的参数

   下面介绍`std::function<>`，看了看，果然是，这样的好处就是参数内存的管理可以放到自己的函数中，不依赖线程池。

   > `std::function` 是 C++ 标准库中的一个模板类，用于表示可调用对象的通用封装。它是 C++11 引入的一部分，为了提供一种灵活的、类型安全的方法来存储、传递和调用各种可调用对象，包括函数指针、函数对象、Lambda 表达式等。

   ```c++
   
   
   #include <iostream>
   #include <functional>
   
   // 定义一个函数
   int add(int a, int b) {
       return a + b;
   }
   
   int main() {
       // 使用 std::function 定义一个可调用对象
       std::function<int(int, int)> addFunction = add;
   
       // 调用可调用对象
       int result = addFunction(2, 3);
   
       std::cout << "Result: " << result << std::endl;
   
       return 0;
   }
   
   ```

2. 这个线程池比较简单，因为没有考虑到线程池的动态伸缩，直接用的是固定的线程池

3. 我到现在对智能指针的使用都看不太懂：

   可以看到他用的智能指针来管理线程池中的线程对象（都是new出来的），因为他的任务队列中的函数都是无参的函数，所以这个线程池的内存管理只需要管理管理线程类就可以。用了智能指针，这个容器销毁的时候会自动销毁这些对象？



## 线程安全的单例类：Singleton

面向对象有个函数，就是你想要你的对象具有什么样的特征，比如之前经常遇到的==可比较，可拷贝==都可以通过继承一些基类从而使得你的类有了这些特征。这里我们经常遇到单例模式的情况，也可以通过继承的方式办到。

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_SINGLETON_H
#define MUDUO_BASE_SINGLETON_H

#include "muduo/base/noncopyable.h"

#include <assert.h>
#include <pthread.h>
#include <stdlib.h> // atexit

namespace muduo
{

namespace detail
{
// This doesn't detect inherited member functions!
// http://stackoverflow.com/questions/1966362/sfinae-to-check-for-inherited-member-functions
template<typename T>
struct has_no_destroy
{
  template <typename C> static char test(decltype(&C::no_destroy));
  template <typename C> static int32_t test(...);
  const static bool value = sizeof(test<T>(0)) == 1;
};
}  // namespace detail

template<typename T>
class Singleton : noncopyable
{
 public:
   //先把你的构造和析构都给禁用了
  Singleton() = delete;
  ~Singleton() = delete;

    //让getinstance只能执行一次
  static T& instance()
  {
    pthread_once(&ponce_, &Singleton::init);
    assert(value_ != NULL);
    return *value_;
  }

 private:
  static void init()
  {
     // 这里的value_是static的，所以只有一份
    value_ = new T();
      
    if (!detail::has_no_destroy<T>::value)
    {
        //程序结束自动调用的函数
      ::atexit(destroy);
    }
  }

  static void destroy()
  {
      //要想销毁这个对象，那这个对象一定是一个完全类型
    typedef char T_must_be_complete_type[sizeof(T) == 0 ? -1 : 1];
      //在编译的时候不完全类型就会让数组编程-1，直接通不过编译
    T_must_be_complete_type dummy; (void) dummy;

    delete value_;
    value_ = NULL;
  }

 private:
  static pthread_once_t ponce_;
  static T*             value_;
};

template<typename T>
pthread_once_t Singleton<T>::ponce_ = PTHREAD_ONCE_INIT;

template<typename T>
T* Singleton<T>::value_ = NULL;

}  // namespace muduo

#endif  // MUDUO_BASE_SINGLETON_H


```

**pthread_once_t**

> `pthread_once_t` 是 POSIX 线程库（pthread）中定义的数据类型之一。它用于实现线程安全的一次性初始化，确保一个特定的函数仅在多线程环境中被执行一次。
>
> 在多线程程序中，有时候需要确保某个初始化操作只被执行一次，而不管有多少个线程在调用。这就是 `pthread_once_t` 所解决的问题。
>
> `pthread_once_t` 类型的变量通常与 `pthread_once` 函数一起使用。`pthread_once` 函数接受一个 `pthread_once_t` 类型的变量，以及一个初始化函数。该函数保证只有在第一次调用 `pthread_once` 时，初始化函数才会被执行，之后即使有多个线程调用，也不再执行初始化函数。

**int pthread_once(pthread_once_t *once_control, void (*init_function)(void))**

> - `once_control`：一个指向 `pthread_once_t` 类型的变量的指针。该变量用于追踪初始化是否已经完成。
> - `init_function`：一个函数指针，指向需要执行的初始化函数。该函数在多线程环境中只会执行一次。
>
> `pthread_once` 的工作原理是，第一次调用时，它会检查 `once_control` 是否已经被初始化。如果没有被初始化，它会调用 `init_function` 执行初始化，并将 `once_control` 标记为已初始化。如果多个线程同时调用 `pthread_once`，只有一个线程会执行初始化函数，其他线程会等待初始化完成。

**完全类型**

> 在销毁一个对象的时候要判断是否是一个完全类型。比如你只是声明了一个类没有实现他。你编译没问题，也可以用指针表示这个类。但是在你要delete的时候就会崩溃。typedef char T_must_be_complete_type[sizeof(T) == 0 ? -1 : 1];这里用了这个方法，让他在编译的时候就给他报错。

**atexit**

> 注册一个函数，在程序结束时候调用，一般是用来销毁资源。

**总结**

单例的目的就是为了让==一个对象在程序中只存在一个==，这和==初始化函数只执行一次不谋而合==



## 私有线程类： ThreadLocal\<T>

- 在单线程的程序中，我们需要用到全局变量，以便我们可以实现多个对象之间的共享数据。
- 在多线程环境下，因为数据空间是共享的，所以全局变量也会被其他线程中的对象所有
- 我们有必要提供线程私有的全局变量，尽在某个线程中有效，但是可以被同一线程中的其他对象访问
- 对于对于每个线程的独有数据，我们把这些数据称之为TSD，TLS（POSIX维护了一定的数据结构来解决这个问题）
- ==对于POD类型的线程的本地存储，可以用__thread关键字来解决，对于非POD类型，可以用TSD来解决==

**头文件**

```c++
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.
//
// Author: Shuo Chen (chenshuo at chenshuo dot com)

#ifndef MUDUO_BASE_THREADLOCAL_H
#define MUDUO_BASE_THREADLOCAL_H

#include "muduo/base/Mutex.h"
#include "muduo/base/noncopyable.h"

#include <pthread.h>

namespace muduo
{

template<typename T>
class ThreadLocal : noncopyable
{
 public:
  ThreadLocal()
  {
    MCHECK(pthread_key_create(&pkey_, &ThreadLocal::destructor));
  }

  ~ThreadLocal()
  {
    MCHECK(pthread_key_delete(pkey_));
  }

  T& value()
  {
    T* perThreadValue = static_cast<T*>(pthread_getspecific(pkey_));
    if (!perThreadValue)
    {
      T* newObj = new T();
        //将这个线程独有的数据放进开辟的空间里面，注意我觉得这个空间只是一个
        //指针（4字节的大小x86）（8字节x64）
      MCHECK(pthread_setspecific(pkey_, newObj));
      perThreadValue = newObj;
    }
    return *perThreadValue;
  }

 private:

  static void destructor(void *x)
  {
    T* obj = static_cast<T*>(x);
      //来了，你看看人家编程多么的严谨，delete外部传过来的指针都要先判断一下是否是完整的数据类型
      //如此良好严谨的编程习惯，多多的学习啊
    typedef char T_must_be_complete_type[sizeof(T) == 0 ? -1 : 1];
    T_must_be_complete_type dummy; (void) dummy;
    delete obj;
  }

 private:
  pthread_key_t pkey_;
};

}  // namespace muduo

#endif  // MUDUO_BASE_THREADLOCAL_H

```

**int pthread_key_create(pthread_key_t *key, void (*destructor)(void*))**

> - `key`：一个指向 `pthread_key_t` 类型的指针，用于存储创建的线程特定数据键的标识符。
> - `destructor`：一个指向函数的指针，该函数在线程退出时被调用，用于清理线程特定数据。可以传入 `NULL`，表示不需要清理函数。
>
> 该函数用于创建线程特定数据键，返回值为 0 表示成功，非零值表示失败。创建线程特定数据键后，可以使用 `pthread_setspecific` 设置线程特定数据的值，并使用 `pthread_getspecific` 获取线程特定数据的值。当线程退出时，如果指定了清理函数，清理函数将被调用。

这个函数主要就是给每个线程都创建了一个指针，你可以用特定的函数对指针指向的区域进行修改，这样就做到了，每个线程都有，但是每隔线程都是独立的数据类型。==但是我记得c++11已经有一个`thread_local`关键字来达到这个效果了==。用来给每隔线程都创建一个独立的空间。

- 出了这个函数还有pthread_key_delete。这个并不是删除这个数据的，数据的删除是create的时候指定的回调函数做的工作。delete的目标是消除这个数据键，如果数据键还有指向数据，可会调用这个构造函数

- 还有对这个区域的值进行获取和修改的函数pthread_getspecific以及pthread_setspesific.
