// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)
//
// This is an internal header file, you should not include this.

#ifndef MUDUO_NET_TIMERQUEUE_H
#define MUDUO_NET_TIMERQUEUE_H

#include <set>
#include <vector>

#include "muduo/base/Mutex.h"
#include "muduo/base/Timestamp.h"
#include "muduo/net/Callbacks.h"
#include "muduo/net/Channel.h"

namespace muduo
{
  namespace net
  {

    class EventLoop;
    class Timer;
    class TimerId;

    ///
    /// A best efforts timer queue.
    /// No guarantee that the callback will be on time.
    ///

    // 这个类有个容器，保存着大量正在使用的计时器
    // 按照到期时间放到容器中，然后把最先到期的设置一个定时器
    // 有插入删除计时器操作，就修改这个容器的排序
    // 到期后，会调用计时器的回调函数
    // 回调函数会看定时器列表有多少个定时器超时了
    // 执行所有定时器的回调事件
    // 重置定时器
    class TimerQueue : noncopyable
    {
    public:
      // 这个是和eventloop绑定的
      explicit TimerQueue(EventLoop *loop);
      ~TimerQueue();

      ///
      /// Schedules the callback to be run at given time,
      /// repeats if @c interval > 0.0.
      ///
      /// Must be thread safe. Usually be called from other threads.
      // 线程安全的
      TimerId addTimer(TimerCallback cb,
                       Timestamp when,
                       double interval);

      // 也可以跨线程调用
      void cancel(TimerId timerId);

    private:
      // FIXME: use unique_ptr<Timer> instead of raw pointers.
      // This requires heterogeneous comparison lookup (N3465) from C++14
      // so that we can find an T* in a set<unique_ptr<T>>.
      // 下面的两个set保存的是相同的东西
      // 不过一个是按照时间排序，另一个按照地址排序
      typedef std::pair<Timestamp, Timer *> Entry;
      typedef std::set<Entry> TimerList;
      typedef std::pair<Timer *, int64_t> ActiveTimer;
      typedef std::set<ActiveTimer> ActiveTimerSet;

      // 以下 的成员函数，只在所属的线程中掉用，所以不必加锁
      void addTimerInLoop(Timer *timer);
      void cancelInLoop(TimerId timerId);
      // called when timerfd alarms
      // 定时器结束后执行这一个函数
      void handleRead();
      // move out all expired timers
      // 返回超时的定时器列表
      std::vector<Entry> getExpired(Timestamp now);
      // 对超时的定时器重置（有的定时器时需要反复激活的）
      void reset(const std::vector<Entry> &expired, Timestamp now);

      // 插入定时器
      bool insert(Timer *timer);

      // 所属的loop
      EventLoop *loop_;
      // 定时器所创建的文件描述符
      const int timerfd_;
      // 定时器的通道（定时器文件描述符的监听）
      Channel timerfdChannel_;
      // Timer list sorted by expiration
      // 按照时间排序的
      TimerList timers_;

      // for cancel()
      // 按照地址排序的
      ActiveTimerSet activeTimers_;
      // 是否正在处理超时的定时器
      bool callingExpiredTimers_; /* atomic */
      // 被取消的定时器
      ActiveTimerSet cancelingTimers_;
    };

  } // namespace net
} // namespace muduo
#endif // MUDUO_NET_TIMERQUEUE_H
