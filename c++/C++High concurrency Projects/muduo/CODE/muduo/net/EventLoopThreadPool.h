// Copyright 2010, Shuo Chen.  All rights reserved.
// http://code.google.com/p/muduo/
//
// Use of this source code is governed by a BSD-style license
// that can be found in the License file.

// Author: Shuo Chen (chenshuo at chenshuo dot com)
//
// This is an internal header file, you should not include this.

#ifndef MUDUO_NET_EVENTLOOPTHREADPOOL_H
#define MUDUO_NET_EVENTLOOPTHREADPOOL_H

#include "muduo/base/noncopyable.h"
#include "muduo/base/Types.h"

#include <functional>
#include <memory>
#include <vector>

namespace muduo
{

  namespace net
  {

    class EventLoop;
    class EventLoopThread;

    class EventLoopThreadPool : noncopyable
    {
    public:
      typedef std::function<void(EventLoop *)> ThreadInitCallback;

      EventLoopThreadPool(EventLoop *baseLoop, const string &nameArg);
      ~EventLoopThreadPool();
      void setThreadNum(int numThreads) { numThreads_ = numThreads; }
      void start(const ThreadInitCallback &cb = ThreadInitCallback());

      // valid after calling start()
      /// round-robin
      EventLoop *getNextLoop();

      /// with the same hash code, it will always return the same EventLoop
      EventLoop *getLoopForHash(size_t hashCode);

      std::vector<EventLoop *> getAllLoops();

      bool started() const
      {
        return started_;
      }

      const string &name() const
      {
        return name_;
      }

    private:
      EventLoop *baseLoop_;
      string name_;
      bool started_;
      // 线程数
      int numThreads_;
      // 当一个新连接到来
      // 选一个线程来处理
      // 表示选择的eventloop对象
      int next_;
      // threaa销毁的时候，它里面的io线程也就自动销毁了
      std::vector<std::unique_ptr<EventLoopThread>> threads_;
      // loop列表
      // 一个io线程对应一个loop对象
      // 这些对象都是栈上的对象，不需要我们管理
      std::vector<EventLoop *> loops_;
    };

  } // namespace net
} // namespace muduo

#endif // MUDUO_NET_EVENTLOOPTHREADPOOL_H
