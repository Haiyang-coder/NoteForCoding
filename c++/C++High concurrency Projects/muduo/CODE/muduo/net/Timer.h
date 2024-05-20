// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)
//
// This is an internal header file, you should not include this.

#ifndef MUDUO_NET_TIMER_H
#define MUDUO_NET_TIMER_H

#include "muduo/base/Atomic.h"
#include "muduo/base/Timestamp.h"
#include "muduo/net/Callbacks.h"

namespace muduo
{
  namespace net
  {

    ///
    /// Internal class for timer event.
    ///
    class Timer : noncopyable
    {
    public:
      Timer(TimerCallback cb, Timestamp when, double interval)
          : callback_(std::move(cb)),
            expiration_(when),
            interval_(interval),
            repeat_(interval > 0.0),
            sequence_(s_numCreated_.incrementAndGet())
      {
      }

      void run() const
      {
        callback_();
      }

      Timestamp expiration() const { return expiration_; }
      bool repeat() const { return repeat_; }
      int64_t sequence() const { return sequence_; }

      void restart(Timestamp now);

      static int64_t numCreated() { return s_numCreated_.get(); }

    private:
      // 定时器到达之后的回调函数
      const TimerCallback callback_;
      // 超时时刻，超时时刻到来的时候，定时器的回调函数会被调用
      Timestamp expiration_;
      // 事件间隔，一次性定时器就是为0
      const double interval_;
      // 是否重复
      const bool repeat_;
      // 定时器序号
      const int64_t sequence_;

      // 定时器计数：当前已经创建好的计时器数量
      // 原子操作类
      static AtomicInt64 s_numCreated_;
    };

  } // namespace net
} // namespace muduo

#endif // MUDUO_NET_TIMER_H
