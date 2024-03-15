// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)

#include "muduo/net/EventLoop.h"

#include "muduo/base/Logging.h"
#include "muduo/base/Mutex.h"
#include "muduo/net/Channel.h"
#include "muduo/net/Poller.h"
#include "muduo/net/SocketsOps.h"
#include "muduo/net/TimerQueue.h"

#include <algorithm>

#include <signal.h>
#include <sys/eventfd.h>
#include <unistd.h>

using namespace muduo;
using namespace muduo::net;

namespace
{
  // 当前线程的eventloop对象的指针
  //__thread 表示线程局部存储的，每个线程会有一个存储空间来存储
  // 否则这个指针变量就成了共享的了
  // 这个变量是全局变量，所以每个线程共享一个，你要是放到类内就要加static
  __thread EventLoop *t_loopInThisThread = 0;

  const int kPollTimeMs = 10000;

  int createEventfd()
  {
    // 在构造函数中直接创建一个eventfd
    // 然后将evtfd放入waitchannel中监听
    int evtfd = ::eventfd(0, EFD_NONBLOCK | EFD_CLOEXEC);
    if (evtfd < 0)
    {
      LOG_SYSERR << "Failed in eventfd";
      abort();
    }
    return evtfd;
  }

#pragma GCC diagnostic ignored "-Wold-style-cast"
  class IgnoreSigPipe
  {
  public:
    IgnoreSigPipe()
    {
      ::signal(SIGPIPE, SIG_IGN);
      // LOG_TRACE << "Ignore SIGPIPE";
    }
  };
#pragma GCC diagnostic error "-Wold-style-cast"

  IgnoreSigPipe initObj;
} // namespace

EventLoop *EventLoop::getEventLoopOfCurrentThread()
{
  return t_loopInThisThread;
}

EventLoop::EventLoop()
    : looping_(false),
      quit_(false),
      eventHandling_(false),
      callingPendingFunctors_(false),
      iteration_(0),
      // 当前线程的id
      threadId_(CurrentThread::tid()),
      poller_(Poller::newDefaultPoller(this)),
      timerQueue_(new TimerQueue(this)),
      wakeupFd_(createEventfd()),
      wakeupChannel_(new Channel(this, wakeupFd_)),
      currentActiveChannel_(NULL)
{
  LOG_DEBUG << "EventLoop created " << this << " in thread " << threadId_;
  if (t_loopInThisThread)
  {
    // 先判定这个线程是否已经有了loop对象，如果已经存在了就直接退出这个线程
    LOG_FATAL << "Another EventLoop " << t_loopInThisThread
              << " exists in this thread " << threadId_;
  }
  else
  {
    // 当前线程的loop对象就是this了
    t_loopInThisThread = this;
  }
  // 在这里设置了唤醒的回调函数
  wakeupChannel_->setReadCallback(
      std::bind(&EventLoop::handleRead, this));
  // we are always reading the wakeupfd
  wakeupChannel_->enableReading();
}

EventLoop::~EventLoop()
{
  LOG_DEBUG << "EventLoop " << this << " of thread " << threadId_
            << " destructs in thread " << CurrentThread::tid();
  wakeupChannel_->disableAll();
  wakeupChannel_->remove();
  ::close(wakeupFd_);
  t_loopInThisThread = NULL;
}

// 事件循环函数，不能跨线程调用
// 你在哪个线程创建了这个对象，你就只能在这个线程中调用这个函数
void EventLoop::loop()
{
  // 是否是在循环中
  assert(!looping_);
  // 判断是否在本线程中
  // 将线程id和动态获取的线程id比较来判断是否是同一个线程
  assertInLoopThread();
  looping_ = true;
  quit_ = false; // FIXME: what if someone calls quit() before loop() ?
  LOG_TRACE << "EventLoop " << this << " start looping";

  while (!quit_)
  {
    // 把通道清理
    activeChannels_.clear();
    // 返回活动的通道
    // 这里的poller就是相当于wait
    // wait有结果之后就封装一个channel返回给你
    // channel里包含了你关注的事件，以及这个事件的回调函数
    pollReturnTime_ = poller_->poll(kPollTimeMs, &activeChannels_);
    ++iteration_;
    if (Logger::logLevel() <= Logger::TRACE)
    {
      // 打印通道
      printActiveChannels();
    }
    // TODO sort channel by priority
    eventHandling_ = true;
    // 遍历通道，处理每个通道
    for (Channel *channel : activeChannels_)
    {
      currentActiveChannel_ = channel;
      // 调用handleevent来处理通道中的事件
      currentActiveChannel_->handleEvent(pollReturnTime_);
    }
    // 处理一轮循环处理完了所有的通道，结束了一轮loop
    currentActiveChannel_ = NULL;
    // 结束了处理通道的状态了
    eventHandling_ = false;
    // 用户给当前io线程的计算任务
    doPendingFunctors();
  }

  LOG_TRACE << "EventLoop " << this << " stop looping";
  // 结束了一次looping了
  looping_ = false;
}

// 该函数可以跨线程调用
void EventLoop::quit()
{
  // 同一个线程能用调用到quit
  // 肯定不是在此线程的loop阻塞的情况下
  // 只能时在回调函数中调用这个quit
  // 完成回调，下一次循环就能关闭这个loop循环了
  quit_ = true;
  // There is a chance that loop() just executes while(!quit_) and exits,
  // then EventLoop destructs, then we are accessing an invalid object.
  // Can be fixed using mutex_ in both places.
  if (!isInLoopThread())
  {
    // 如果是跨线程调用，可能loop正处在阻塞状态或者处理事件的状态
    // 看一下loop函数的具体实现
    // 所以会出现接收不到quit信号的情况
    // 这种情况我们需要唤醒loop循环
    // 原理就是让监听阻塞函数多监听一个管道，通过管道唤醒阻塞
    wakeup();
  }
}

// 这个函数的目的是
// 同一个线程的回调直接就执行了
// 不是同一个线程添加的回调会统一放进容器中
void EventLoop::runInLoop(Functor cb)
{
  // 在io线程中执行某个回调函数，该函数可以跨线程调用
  if (isInLoopThread())
  {
    cb();
  }
  else
  {
    // 异步的将回调函数添加到队列
    queueInLoop(std::move(cb));
  }
}

void EventLoop::queueInLoop(Functor cb)
{
  {
    MutexLockGuard lock(mutex_);
    pendingFunctors_.push_back(std::move(cb));
  }

  // 跨线程调用，唤醒这个线程来执行任务
  if (!isInLoopThread() || callingPendingFunctors_)
  {
    // callingPendingFunctors_为什么这里要唤醒呢
    // loop线程正在处理其他线程添加的回调任务呢，你这时候突然添加任务进来了
    // 处理完就阻塞，你的任务就不能得到执行了
    // 这时候唤醒，紧接着的下一次循环的时候就可以处理你的任务了
    wakeup();
  }
}

size_t EventLoop::queueSize() const
{
  MutexLockGuard lock(mutex_);
  return pendingFunctors_.size();
}

TimerId EventLoop::runAt(Timestamp time, TimerCallback cb)
{
  return timerQueue_->addTimer(std::move(cb), time, 0.0);
}

TimerId EventLoop::runAfter(double delay, TimerCallback cb)
{
  Timestamp time(addTime(Timestamp::now(), delay));
  return runAt(time, std::move(cb));
}

TimerId EventLoop::runEvery(double interval, TimerCallback cb)
{
  Timestamp time(addTime(Timestamp::now(), interval));
  return timerQueue_->addTimer(std::move(cb), time, interval);
}

void EventLoop::cancel(TimerId timerId)
{
  return timerQueue_->cancel(timerId);
}

void EventLoop::updateChannel(Channel *channel)
{
  // 最后是调用了poller_的channel
  assert(channel->ownerLoop() == this);
  assertInLoopThread();
  poller_->updateChannel(channel);
}

void EventLoop::removeChannel(Channel *channel)
{
  assert(channel->ownerLoop() == this);
  assertInLoopThread();
  if (eventHandling_)
  {
    assert(currentActiveChannel_ == channel ||
           std::find(activeChannels_.begin(), activeChannels_.end(), channel) == activeChannels_.end());
  }
  poller_->removeChannel(channel);
}

bool EventLoop::hasChannel(Channel *channel)
{
  assert(channel->ownerLoop() == this);
  assertInLoopThread();
  return poller_->hasChannel(channel);
}

void EventLoop::abortNotInLoopThread()
{
  LOG_FATAL << "EventLoop::abortNotInLoopThread - EventLoop " << this
            << " was created in threadId_ = " << threadId_
            << ", current thread id = " << CurrentThread::tid();
}

void EventLoop::wakeup()
{
  // eventfd 只有八个字节的缓冲区
  // 往这缓冲区中写入八个字节
  // 在退出loop的时候调用一下，可以激活其他线程
  uint64_t one = 1;
  ssize_t n = sockets::write(wakeupFd_, &one, sizeof one);
  if (n != sizeof one)
  {
    LOG_ERROR << "EventLoop::wakeup() writes " << n << " bytes instead of 8";
  }
}

void EventLoop::handleRead()
{
  // 很简单就是读一下，将信号水平
  uint64_t one = 1;
  ssize_t n = sockets::read(wakeupFd_, &one, sizeof one);
  if (n != sizeof one)
  {
    LOG_ERROR << "EventLoop::handleRead() reads " << n << " bytes instead of 8";
  }
}

void EventLoop::doPendingFunctors()
{
  std::vector<Functor> functors;
  callingPendingFunctors_ = true;

  {
    MutexLockGuard lock(mutex_);
    // 拷贝出来，加锁，然后在用里面的东西，就不用被锁竞争搞得效率下降
    functors.swap(pendingFunctors_);
  }

  // fucntor这个方法可能还会再次调用 queueInLoop
  // 这是queueInLoop必须调用wakeup，否则新增的函数就不能及时调用了
  for (const Functor &functor : functors)
  {
    functor();
  }
  callingPendingFunctors_ = false;
}

void EventLoop::printActiveChannels() const
{
  for (const Channel *channel : activeChannels_)
  {
    LOG_TRACE << "{" << channel->reventsToString() << "} ";
  }
}
